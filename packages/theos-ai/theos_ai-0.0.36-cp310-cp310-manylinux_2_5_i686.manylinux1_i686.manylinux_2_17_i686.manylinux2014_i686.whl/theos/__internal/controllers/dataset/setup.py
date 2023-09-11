from theos.__internal.connectors import dataset as dataset_connector, constants as connector_constants
from theos.__internal.data.persistance import api as api_persistance
from theos.__internal.utils.io import operations as io_operations
from theos.computer_vision.object_detection.utils import crop
from theos.__internal.utils import other, http, system, log
from theos.__internal.utils.io import info as io_info
from theos.__internal.data import config, environment
import yaml
from pathlib import Path
from tqdm import tqdm
import asyncio
import time
import json
import cv2
import os

intervals = (
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hours', 3600),    # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
)


def display_time(seconds, granularity=2):
    result = []
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result)

def create_configuration_file(manifest, dataset_name, target_dataset_path):
    dataset_classes = manifest['classes']
    classes = []
    
    for dataset_class in dataset_classes:
        if not dataset_class['is_superclass']:
            classes.append({'name':dataset_class['name'], 'color':dataset_class['color']})
    
    configuration = {
        'name':dataset_name,
        'train':'train/images',
        'val':'valid/images',
        'test':'test/images',
        'nc':len(classes),
        'classes':classes
    }

    configuration_path = system.join_paths(target_dataset_path, 'configuration.yaml')
    if io_info.file_exists(configuration_path):
        io_operations.remove_file(configuration_path)
    io_operations.save_data_to_yaml_file(configuration_path, configuration)


                
class FlowList(list):
    pass

def flow_list_rep(dumper, data):
    return dumper.represent_sequence(u'tag:yaml.org,2002:seq', data, flow_style=True)

yaml.add_representer(FlowList, flow_list_rep)


def create_yolov8_configuration_file(manifest, dataset_name, target_dataset_path, kpt_shape, flip_idx):
    dataset_classes = manifest['classes']
    classes = {}
    idx = 0
    for dataset_class in dataset_classes:
        if not dataset_class['is_superclass']:
            classes[idx] = dataset_class['name']
            idx += 1

    if kpt_shape is None or flip_idx is None:
        configuration = {
            'path': '',
            'train': 'train/images',  # train images (relative to 'path')
            'val': 'valid/images',  # val images (relative to 'path')
            'test': 'test/images',  # test images (optional)
            'names': classes  # classes dictionary
        }
    else:
        configuration = {
            'path': '',
            'train': 'train/images',  # train images (relative to 'path')
            'val': 'valid/images',  # val images (relative to 'path')
            'test': 'test/images',  # test images (optional)
            'kpt_shape': FlowList(kpt_shape),  # number of keypoints, number of dims
            'flip_idx': FlowList(flip_idx),  # flip index
            'names': classes  # classes dictionary
        }

    configuration_path = os.path.join(target_dataset_path, 'configuration.yaml')
    if os.path.exists(configuration_path):
        os.remove(configuration_path)
        
    with open(configuration_path, 'w') as yaml_file:
        yaml.dump(configuration, yaml_file, default_flow_style=False)


class DatasetInstaller:
    def __init__(self, args, remote=None, retry=False, parallel_files_count=500, max_tries=100):
        self.args = args
        self.remote = remote
        self.retry = retry
        self.parallel_files_count = parallel_files_count
        self.max_tries = max_tries
        self.installing = False
        self.task = None
        self.loop = asyncio.get_event_loop()
    
    async def cancel(self):
        self.task.cancel()

    async def install(self):
        self.installing = True
        self.files_downloading_count = 0
        self.task = self.loop.create_task(self.__install())
        self.download_flag = asyncio.Event()
        self.download_flag.set()
    
    async def download_file(self, file_url, file_path, pbar=None):
        await http.download_file_from_url(file_url, file_path, with_progress_bar=False, resume=False, retry=True, pbar=pbar)
        self.files_downloading_count -= 1
        self.download_flag.set()

    async def __install(self):
        if self.remote:
            self.args = other.DictionaryObject(self.args)
            await self.remote['send_status'](connector_constants.PULLING_DATASET, self.remote['channel_name'])
        
        dataset_path = system.join_paths(config.get_system_folder_path(), self.args.field_path_name, self.args.subfield_path_name, 'datasets', self.args.dataset, 'formats', config.dataset_format_path_name)
        io_operations.create_folder_if_it_doesnt_exist(dataset_path)

        if system.is_inside_gcloud_vm():
            log.info(f'pulling {self.args.dataset} dataset...')
            api = api_persistance.get()
            api_version = api.get_version()
            start_time = time.time()
            dataset_bucket_path = f'gs://theos-{environment.NAME}-{api_version}/projects/{self.args.project_id}/datasets/{self.args.dataset_id}'
            system.run_command(f'gcloud alpha storage cp -r {dataset_bucket_path}/train {dataset_bucket_path}/valid {dataset_bucket_path}/test {dataset_path}')
            manifest = {'files':[], 'classes':self.args.classes}
            io_operations.save_json_to_new_file(system.join_paths(dataset_path, 'manifest.json'), manifest)
            create_configuration_file(manifest, self.args.dataset, dataset_path)
            end_time = time.time()
            seconds_elapsed = end_time - start_time
            elapsed_time = display_time(seconds_elapsed)

            if not elapsed_time:
                elapsed_time = 'less than a second'

            log.info(f'{self.args.dataset} dataset pulled successfully in {elapsed_time}')
        else:
            ok = False
            tries = 0

            while not ok and tries < self.max_tries:
                try:
                    dataset_manifest_url = dataset_connector.get_dataset_manifest_url(self.args.project_id, self.args.dataset)
                    ok = len(dataset_manifest_url) > 0
                except:
                    tries += 1
                    log.error('manifest creation error. Trying again...')
                    await asyncio.sleep(1)
    
            manifest_path = system.join_paths(dataset_path, 'manifest.json')
            old_manifest = None
            old_manifest_files = None
            old_files_paths = []
            old_manifest_path = ''
            
            if io_info.file_exists(manifest_path):
                old_manifest_path = system.join_paths(dataset_path, 'old_manifest.json')
                io_operations.rename_file(manifest_path, old_manifest_path)
                old_manifest = io_operations.get_json_data_from_file(old_manifest_path)
                old_manifest_files = old_manifest['files']
                old_files_paths = old_manifest_files.keys()
            
            log.info(f'downloading {self.args.dataset} dataset manifest:')
            ok = False
            tries = 0
            
            while not ok and tries < self.max_tries:
                try:
                    await http.download_file_from_url(dataset_manifest_url, manifest_path, resume=False)
                    ok = True
                except:
                    log.error('dataset manifest download error. Trying again...')
                    tries += 1
                    await asyncio.sleep(1)

            manifest = io_operations.get_json_data_from_file(manifest_path)
            create_configuration_file(manifest, self.args.dataset, dataset_path)
            manifest_files = manifest['files']
            files_paths = manifest_files.keys()
            files_count = len(files_paths)
            log.info(f'pulling {self.args.dataset} dataset:')
            print()
            pbar = tqdm(total=files_count)
            start_time = time.time()
            new_files_count = 0
            deleted_files_count = 0
            modified_files_count = 0

            for old_file_path in old_files_paths:
                old_splitted_path = old_file_path.split('/')
                full_old_file_path = system.join_paths(dataset_path, *old_splitted_path)
                if (old_file_path not in files_paths) and io_info.file_exists(full_old_file_path):
                    io_operations.remove_file(full_old_file_path)
                    deleted_files_count += 1

            for file_path in files_paths:
                splitted_path = file_path.split('/')
                full_folder_path = system.join_paths(dataset_path, *splitted_path[:-1])
                full_file_path = system.join_paths(dataset_path, *splitted_path)
                file_metadata = manifest_files[file_path]
                file_url = file_metadata['url']
                file_etag = file_metadata['etag']
                needs_download = True
                
                if file_path in old_files_paths:
                    old_file_metadata = old_manifest_files[file_path]
                    old_file_etag = old_file_metadata['etag']
                    if old_file_etag == file_etag:
                        needs_download = False
                    elif io_info.file_exists(full_file_path):
                        io_operations.remove_file(full_file_path)
                        modified_files_count += 1
                else:
                    new_files_count += 1
                
                io_operations.create_folder_if_it_doesnt_exist(full_folder_path)

                if needs_download:
                    if self.files_downloading_count + 1 > self.parallel_files_count:
                        self.download_flag.clear()
                        await self.download_flag.wait()
                    
                    self.files_downloading_count += 1
                    self.loop.create_task(self.download_file(file_url, full_file_path, pbar=pbar))
            
            while self.files_downloading_count > 0:
                await asyncio.sleep(1)

            if old_manifest_path:
                io_operations.remove_file(old_manifest_path)

            pbar.update(files_count - pbar.n)
            pbar.close()
            end_time = time.time()
            seconds_elapsed = end_time - start_time
            elapsed_time = display_time(seconds_elapsed)

            if not elapsed_time:
                elapsed_time = 'less than a second'

            print()
            log.info(f'{self.args.dataset} dataset pulled successfully in {elapsed_time}:')
            print()
            print(f'{new_files_count} new')
            print(f'{deleted_files_count} deleted')
            print(f'{modified_files_count} modified')
            print()
        
        self.installing = False
        if self.remote:
            await self.remote['send_status'](connector_constants.DATASET_PULLED, self.remote['channel_name'])


class DatasetTranslator:
    def __init__(self, args, remote=None, retry=False, from_cli=False):
        self.args = args
        self.remote = remote
        self.retry = retry
        self.from_cli = from_cli
        self.translating = False
        self.task = None
        self.loop = asyncio.get_event_loop()

    async def cancel(self):
        self.task.cancel()

    async def translate(self):
        self.translating = True
        self.task = self.loop.create_task(self.__translate())
    
    async def __translate(self):
        if self.remote:
            self.args = other.DictionaryObject(self.args)
            await self.remote['send_status'](connector_constants.TRANSLATING_DATASET, self.remote['channel_name'])
        
        if not self.from_cli:
            source_dataset_path = system.join_paths(config.get_system_folder_path(), self.args.field_path_name, self.args.subfield_path_name, 'datasets', self.args.dataset, 'formats', config.dataset_format_path_name)
            target_dataset_path = system.join_paths(config.get_system_folder_path(), self.args.field_path_name, self.args.subfield_path_name, 'datasets', self.args.dataset, 'formats', self.args.label_format)
            label_format = self.args.label_format
        else:
            source_dataset_path = self.args.input
            target_dataset_path = self.args.output
            label_format = self.args.format

        if io_info.folder_exists(target_dataset_path):
            io_operations.remove_folder(target_dataset_path)

        if label_format == 'yolo_darknet':
            await self.__to_yolo_darknet(source_dataset_path, target_dataset_path)
        elif label_format == 'yolov8':
            await self.__to_yolov8(source_dataset_path, target_dataset_path)
        elif label_format == 'coco2017':
            await self.__to_coco2017(source_dataset_path, target_dataset_path)
        elif label_format == 'paddleocr':
            await self.__to_paddle_ocr(source_dataset_path, target_dataset_path)
        
        log.info('dataset translated successfully')
        
        self.translating = False
        if self.remote:
            await self.remote['send_status'](connector_constants.DATASET_TRANSLATED, self.remote['channel_name'])

    async def __to_paddle_ocr(self, source_dataset_path, target_dataset_path):
        log.info('translating dataset to PaddleOCR format...')
        print()
        io_operations.create_folder_if_it_doesnt_exist(system.join_paths(target_dataset_path, 'train'))
        io_operations.create_folder_if_it_doesnt_exist(system.join_paths(target_dataset_path, 'eval'))
        files_paths = list(Path(source_dataset_path).rglob('*'))
        examples = {}
        script_path = os.path.abspath(__file__)
        script_dir = os.path.dirname(script_path)
        filename = 'en_ocr_dict.txt'
        file_path = os.path.join(script_dir, filename)

        with open(file_path, 'r') as file:
            lines = file.readlines()

        english_dictionary = [line.rstrip() for line in lines]
        dictionary = english_dictionary.copy()
        
        for file_path in files_paths:
            if file_path.is_file():
                name, extension = os.path.splitext(file_path.name)
                if file_path.suffix == '.json':
                    if name != 'classes':
                        if name not in examples:
                            examples[name] = {'image':None, 'label':None}
                        examples[name]['label'] = file_path
                else:
                    if name not in examples:
                        examples[name] = {'image':None, 'label':None}
                    
                    examples[name]['image'] = file_path
                    examples[name]['image_extension'] = extension
                    examples[name]['split'] = 'train' if 'train/' in str(file_path) else 'eval'

        labels_txt_files = {
            'train':open(system.join_paths(target_dataset_path, 'train', 'labels.txt'), 'w'),
            'eval':open(system.join_paths(target_dataset_path, 'eval', 'labels.txt'), 'w')
        }

        for name in tqdm(examples):
            example = examples[name]
            if example['label'] is not None and example['image'] is not None:
                split = example['split']
                labels = io_operations.get_json_data_from_file(example['label'])
                image = None
                label_number = 1
                for label in labels:
                    if 'text' in label and len(label['text']) > 0:
                        if image is None:
                            image = cv2.imread(str(example['image']))
                        
                        label['x'] = int(label['x'])
                        label['y'] = int(label['y'])
                        label['width'] = int(label['width'])
                        label['height'] = int(label['height'])

                        text_image = crop(image, label)
                        extension = example['image_extension']
                        text_image_name = f'{name}-{label_number}{extension}'
                        text = label['text']
                        # for character in text:
                        #     if character not in dictionary:
                        #         dictionary.append(character)
                        cv2.imwrite(system.join_paths(target_dataset_path, split, text_image_name), text_image)
                        labels_txt_files[split].write(f'{text_image_name}\t {text}\n')
                        label_number += 1
        print()

        with open(system.join_paths(target_dataset_path, 'dictionary.txt'), 'w') as dictionary_txt_file:
            for character in dictionary:
                dictionary_txt_file.write(f'{character}\n')
    
    async def __to_yolov8(self, source_dataset_path, target_dataset_path):
        manifest_path = system.join_paths(source_dataset_path, 'manifest.json')
        manifest = io_operations.get_json_data_from_file(manifest_path)
        class_id_mapping = {}
        dataset_classes = manifest['classes']
        mapped_id = 0

        for dataset_class in dataset_classes:
            if not dataset_class['is_superclass']:
                class_id_mapping[dataset_class['id']] = mapped_id
                mapped_id += 1

        for split in ['train', 'test', 'valid']:
            source_split_path = system.join_paths(source_dataset_path, split)
            target_split_path = system.join_paths(target_dataset_path, split)
            io_operations.create_folder_if_it_doesnt_exist(target_split_path)
            source_images_path = system.join_paths(source_split_path, 'images')
            target_images_path = system.join_paths(target_split_path, 'images')
            kpt_shape = None
            flip_idx = None
            if self.from_cli:
                log.info(f'copying dataset {split} images to yolov8 folder...')
            else:
                log.info(f'copying {self.args.dataset} dataset {split} images to yolov8 folder...')
            io_operations.copy_folder(source_images_path, target_images_path)

            source_labels_path = system.join_paths(source_split_path, 'labels')
            target_labels_path = system.join_paths(target_split_path, 'labels')
            io_operations.create_folder_if_it_doesnt_exist(target_labels_path)

            images = io_info.list_folder(source_images_path)

            if self.from_cli:
                log.info(f'translating dataset {split} labels:')
            else:
                log.info(f'translating {self.args.dataset} dataset {split} labels:')
            print()

            for image in tqdm(images):
                full_image_file_name = io_info.decode_file_name(image)
                image_file_name = io_info.get_file_name(full_image_file_name)
                source_label_path = system.join_paths(source_labels_path, image_file_name + '.json')
                
                if io_info.file_exists(source_label_path):
                    target_label_path = system.join_paths(target_labels_path, image_file_name + '.txt')
                    source_image_path = system.join_paths(source_images_path, full_image_file_name)
                    image_labels = io_operations.get_json_data_from_file(source_label_path)
                    width, height = io_info.get_image_size(source_image_path)
                    translated_labels = []

                    for i, image_label in enumerate(image_labels):
                        class_id = class_id_mapping[image_label['class_id']]
                        top_left_point_x = image_label['x']
                        top_left_point_y = image_label['y']
                        label_width = image_label['width']
                        label_height = image_label['height']
                        x_center = (top_left_point_x + label_width/2)/width
                        y_center = (top_left_point_y + label_height/2)/height
                        label_width /= width
                        label_height /= height
                        if 'keypoints' in image_label:
                            keypoints = []
                            for keypoint in image_label['keypoints']:
                                try:
                                    kp_x = keypoint['x']/width
                                    kp_y = keypoint['y']/height
                                    visibility = int(keypoint['visible'])
                                    keypoints.append(f"{kp_x} {kp_y} {visibility}")
                                except:
                                    print('error')
                                    print(source_label_path)

                            translated_labels.append(f'{class_id} {x_center} {y_center} {label_width} {label_height} {" ".join(keypoints)}')
                        else:
                            translated_labels.append(f'{class_id} {x_center} {y_center} {label_width} {label_height}')

                    if len(translated_labels) > 0:
                        txt_data = '\n'.join(translated_labels)
                        io_operations.save_to_txt_file(target_label_path, txt_data)
                        
                    if len(image_labels) > 0 and 'keypoints' in image_labels[0]:
                        kpt_shape = [len(image_labels[0]['keypoints']), 3]
                        flip_idx = list(range(kpt_shape[0]))  

            print()
        
        create_yolov8_configuration_file(manifest, self.args.dataset if not self.from_cli else source_dataset_path, target_dataset_path, kpt_shape, flip_idx)

    async def __to_coco2017(self, source_dataset_path, target_dataset_path):
        manifest_path = system.join_paths(source_dataset_path, 'manifest.json')
        manifest = io_operations.get_json_data_from_file(manifest_path)

        coco_format = {
            "info": {},
            "images": [],
            "annotations": [],
            "categories": []
        }

        class_id_mapping = {}
        dataset_classes = manifest['classes']
        mapped_id = 0

        for dataset_class in dataset_classes:
            if not dataset_class['is_superclass']:
                class_id_mapping[dataset_class['id']] = mapped_id
                coco_format["categories"].append({
                    "id": mapped_id,
                    "name": dataset_class["name"],
                    "supercategory": "none",
                    "keypoints": [],  # Fill this with keypoint names if available.
                    "skeleton": []  # Typically, pairs of keypoint indices forming the skeleton.
                })
                mapped_id += 1

        annotation_id = 0
        for split in ['train', 'test', 'valid']:
            source_split_path = system.join_paths(source_dataset_path, split)
            source_images_path = system.join_paths(source_split_path, 'images')
            source_labels_path = system.join_paths(source_split_path, 'labels')

            images = io_info.list_folder(source_images_path)

            for image_id, image in enumerate(images):
                full_image_file_name = io_info.decode_file_name(image)
                image_file_name = io_info.get_file_name(full_image_file_name)
                label_file_path = system.join_paths(source_labels_path, image_file_name + '.json')

                if io_info.file_exists(label_file_path):
                    source_image_path = system.join_paths(source_images_path, full_image_file_name)
                    width, height = io_info.get_image_size(source_image_path)

                    coco_format["images"].append({
                        "file_name": image_file_name,
                        "height": height,
                        "width": width,
                        "id": image_id
                    })

                    image_labels = io_operations.get_json_data_from_file(label_file_path)
                    # print(image_label)
                    for i, image_label in enumerate(image_labels):
                        class_id = class_id_mapping[image_label['class_id']]
                        bbox = [image_label['x'], image_label['y'], image_label['width'], image_label['height']]
                        keypoints_list = []
                        if 'keypoints' in image_label and image_label['keypoints']:
                            for keypoint in image_label['keypoints']:
                                visibility = 2 if keypoint["visible"] else 0
                                keypoints_list.extend([keypoint['x'], keypoint['y'], visibility])

                        coco_annotation = {
                            "id": annotation_id,
                            "image_id": image_id,
                            "category_id": class_id,
                            "bbox": bbox,
                            "area": bbox[2] * bbox[3],
                            "iscrowd": 0
                        }

                        if keypoints_list:
                            coco_annotation["keypoints"] = keypoints_list

                        if 'segmentation' in image_label:
                            coco_annotation['segmentation'] = image_label['segmentation']

                        coco_format["annotations"].append(coco_annotation)
                        annotation_id += 1

        if not os.path.exists(target_dataset_path):
            os.makedirs(target_dataset_path)

        with open(system.join_paths(target_dataset_path, "annotations.json"), 'w') as coco_file:
            json.dump(coco_format, coco_file)

    async def __to_yolo_darknet(self, source_dataset_path, target_dataset_path):
        manifest_path = system.join_paths(source_dataset_path, 'manifest.json')
        manifest = io_operations.get_json_data_from_file(manifest_path)
        class_id_mapping = {}
        dataset_classes = manifest['classes']
        mapped_id = 0

        for dataset_class in dataset_classes:
            if not dataset_class['is_superclass']:
                class_id_mapping[dataset_class['id']] = mapped_id
                mapped_id += 1

        for split in ['train', 'test', 'valid']:
            source_split_path = system.join_paths(source_dataset_path, split)
            target_split_path = system.join_paths(target_dataset_path, split)
            io_operations.create_folder_if_it_doesnt_exist(target_split_path)
            source_images_path = system.join_paths(source_split_path, 'images')
            target_images_path = system.join_paths(target_split_path, 'images')
            if self.from_cli:
                log.info(f'copying dataset {split} images to yolo_darknet folder...')
            else:
                log.info(f'copying {self.args.dataset} dataset {split} images to yolo_darknet folder...')
            io_operations.copy_folder(source_images_path, target_images_path)

            source_labels_path = system.join_paths(source_split_path, 'labels')
            target_labels_path = system.join_paths(target_split_path, 'labels')
            io_operations.create_folder_if_it_doesnt_exist(target_labels_path)

            images = io_info.list_folder(source_images_path)

            if self.from_cli:
                log.info(f'translating dataset {split} labels:')
            else:
                log.info(f'translating {self.args.dataset} dataset {split} labels:')
            print()

            for image in tqdm(images):
                full_image_file_name = io_info.decode_file_name(image)
                image_file_name = io_info.get_file_name(full_image_file_name)
                source_label_path = system.join_paths(source_labels_path, image_file_name + '.json')
                if io_info.file_exists(source_label_path):
                    target_label_path = system.join_paths(target_labels_path, image_file_name + '.txt')
                    source_image_path = system.join_paths(source_images_path, full_image_file_name)
                    image_labels = io_operations.get_json_data_from_file(source_label_path)
                    width, height = io_info.get_image_size(source_image_path)
                    translated_labels = []

                    for image_label in image_labels:
                        class_id = class_id_mapping[image_label['class_id']]
                        top_left_point_x = image_label['x']
                        top_left_point_y = image_label['y']
                        label_width = image_label['width']
                        label_height = image_label['height']
                        x_center = (top_left_point_x + label_width/2)/width
                        y_center = (top_left_point_y + label_height/2)/height
                        label_width /= width
                        label_height /= height
                        translated_labels.append(f'{class_id} {x_center} {y_center} {label_width} {label_height}')

                    if len(translated_labels) > 0:
                        txt_data = '\n'.join(translated_labels)
                        io_operations.save_to_txt_file(target_label_path, txt_data)

            print()
        
        create_configuration_file(manifest, self.args.dataset if not self.from_cli else source_dataset_path, target_dataset_path)
import unittest
import json
import tempfile
import pathlib
import PIL.Image
import torch
from irisml.tasks.export_coco_from_torch_dataset import Task


class FakeDataset(torch.utils.data.Dataset):
    def __init__(self, data):
        self._data = data

    def __len__(self):
        return len(self._data)

    def __getitem__(self, index):
        return self._data[index]


class TestExportCOCOJsonFromDataset(unittest.TestCase):
    def test_classification(self):
        width = height = 10
        multiclass_dataset = FakeDataset([(PIL.Image.new('RGB', (width, height)), [0]), (PIL.Image.new('RGB', (width, height)), 1)])

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = pathlib.Path(temp_dir)
            Task(Task.Config(task_type='classification_multiclass', dirpath=temp_dir)).execute(Task.Inputs(dataset=multiclass_dataset, class_names=["dog", "cat"]))
            with open(temp_dir / 'images.json') as f:
                coco = json.load(f)
                self.assertDictEqual(coco['images'][0], {"id": 1, "width": width, "height": height, "file_name": 'images/1.png'})
                self.assertDictEqual(coco['annotations'][1], {"id": 2, "category_id": 2, "image_id": 2})
                self.assertDictEqual(coco['categories'][1], {"id": 2, "name": "cat"})

        multilabel_dataset = FakeDataset([(PIL.Image.new('RGB', (width, height)), torch.tensor([i, 1-i])) for i in range(2)])
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = pathlib.Path(temp_dir)
            json_file_name = 'foo'
            Task(Task.Config(task_type='classification_multilabel', json_file_name=json_file_name, dirpath=temp_dir)).execute(Task.Inputs(dataset=multilabel_dataset, class_names=["dog", "cat"]))
            coco = json.loads((temp_dir / f'{json_file_name}.json').read_text())
            self.assertDictEqual(coco['annotations'][0], {"id": 1, "category_id": 1, "image_id": 1})
            self.assertDictEqual(coco['annotations'][1], {"id": 2, "category_id": 2, "image_id": 1})

    def test_object_detection(self):
        width = height = 10
        dataset = FakeDataset([(torch.zeros((3, height, width)), torch.tensor([[0, 0.1, 0.1, 0.2, 0.2], [1, 0.1, 0.1, 0.2, 0.2]])),
                               (torch.zeros((3, height, width)), [[0, 0.1, 0.1, 0.2, 0.2]]),
                               (torch.zeros((3, height, width)), torch.tensor([]))])
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = pathlib.Path(temp_dir)
            image_directory_name = json_file_name = 'foo'

            Task(Task.Config(task_type='object_detection', image_directory_name=image_directory_name, json_file_name=json_file_name, dirpath=temp_dir)).execute(Task.Inputs(dataset, ["dog", "cat"]))
            coco = json.loads((temp_dir / f'{json_file_name}.json').read_text())
            self.assertEqual(len(coco['images']), 3)
            self.assertEqual(len(coco['annotations']), 3)
            self.assertDictEqual(coco['images'][0], {"id": 1, "width": width, "height": height, "file_name": f'{image_directory_name}/1.png'})
            self.assertDictEqual(coco['categories'][1], {"id": 2, "name": "cat"})

            anno = coco['annotations'][1]
            anno['bbox'] = [round(t) for t in anno['bbox']]
            self.assertDictEqual(anno, {"id": 2, "category_id": 2, "image_id": 1, "bbox": [1, 1, 1, 1]})

            anno = coco['annotations'][2]
            anno['bbox'] = [round(t) for t in anno['bbox']]
            self.assertDictEqual(anno, {"id": 3, "category_id": 1, "image_id": 2, "bbox": [1, 1, 1, 1]})

import unittest
import unittest.mock
import PIL.Image
import torch
from irisml.tasks.make_classification_dataset_from_object_detection import Task
from utils import FakeDataset


class FakeDatasetWithGetTargets(torch.utils.data.Dataset):
    def __init__(self, targets):
        self._targets = targets
        self.reset()

    def __len__(self):
        return len(self._targets)

    def __getitem__(self, index):
        self._getitem_args.append(index)
        return PIL.Image.new('RGB', (8, 8)), self._targets[index]

    def get_targets(self, index):
        self._get_targets_args.append(index)
        return self._targets[index]

    def reset(self):
        self._getitem_args = []
        self._get_targets_args = []


class TestMakeClassificationDatasetFromObjectDetection(unittest.TestCase):
    def test_simple(self):
        fake_image = PIL.Image.new('RGB', (32, 32))
        dataset = FakeDataset([(fake_image, torch.tensor([[0, 0, 0, 0.5, 0.5], [1, 0, 0, 0.1, 0.1]])),
                               (fake_image, torch.zeros(0, 5)),
                               (fake_image, torch.tensor([[2, 0, 0, 0.5, 0.5], [3, 0, 0, 0.1, 0.1]])),
                               (fake_image, torch.zeros(0, 5))])

        outputs = Task(Task.Config()).execute(Task.Inputs(dataset))
        self.assertEqual(len(outputs.dataset), 4)
        self.assertEqual(outputs.dataset[0][0].size, (16, 16))
        self.assertEqual(outputs.dataset[0][1], 0)
        self.assertEqual(outputs.dataset[1][0].size, (3, 3))
        self.assertEqual(outputs.dataset[1][1], 1)
        self.assertEqual(outputs.dataset[2][0].size, (16, 16))
        self.assertEqual(outputs.dataset[2][1], 2)
        self.assertEqual(outputs.dataset[3][0].size, (3, 3))
        self.assertEqual(outputs.dataset[3][1], 3)
        self.assertEqual(outputs.index_mappings, [(0, 0), (0, 1), (2, 0), (2, 1)])

    def test_given_multiclass_dataset(self):
        fake_image = PIL.Image.new('RGB', (32, 32))
        dataset = FakeDataset([(fake_image, torch.tensor(0)),
                               (fake_image, torch.tensor(1))])
        outputs = Task(Task.Config()).execute(Task.Inputs(dataset))
        self.assertEqual(len(outputs.dataset), 2)
        self.assertEqual(outputs.dataset[0][0].size, (32, 32))
        self.assertEqual(outputs.dataset[0][1], 0)
        self.assertEqual(outputs.dataset[1][1], 1)
        self.assertIsNone(outputs.index_mappings)

    def test_given_multilabel_dataset(self):
        fake_image = PIL.Image.new('RGB', (32, 32))
        dataset = FakeDataset([(fake_image, torch.tensor([0, 1])),
                               (fake_image, torch.tensor([2, 3, 4]))])
        outputs = Task(Task.Config()).execute(Task.Inputs(dataset))
        self.assertEqual(len(outputs.dataset), 2)
        self.assertEqual(outputs.dataset[0][0].size, (32, 32))
        self.assertEqual(outputs.dataset[0][1].dim(), 1)
        self.assertEqual(outputs.dataset[1][1][2], 4)
        self.assertIsNone(outputs.index_mappings)

    def test_get_targets(self):
        dataset = FakeDatasetWithGetTargets([torch.tensor([[0, 0, 0, 0.5, 0.5], [1, 0, 0, 0.1, 0.1]]), torch.tensor([[0, 0, 0, 1, 1]]), torch.empty(0, 5)])

        outputs = Task(Task.Config()).execute(Task.Inputs(dataset))
        self.assertEqual(dataset._getitem_args, [0])
        self.assertEqual(dataset._get_targets_args, [0, 1, 2])
        self.assertEqual(len(outputs.dataset), 3)

        dataset.reset()
        self.assertEqual(outputs.dataset.get_targets(0), torch.tensor(0))
        self.assertEqual(outputs.dataset.get_targets(1), torch.tensor(1))
        self.assertEqual(outputs.dataset.get_targets(2), torch.tensor(0))
        self.assertEqual(dataset._getitem_args, [])
        self.assertEqual(dataset._get_targets_args, [0, 0, 1])

        dataset.reset()
        self.assertEqual(outputs.dataset[0][1], torch.tensor(0))
        self.assertEqual(outputs.dataset[1][1], torch.tensor(1))
        self.assertEqual(outputs.dataset[2][1], torch.tensor(0))
        self.assertEqual(dataset._getitem_args, [0, 0, 1])
        self.assertEqual(dataset._get_targets_args, [])

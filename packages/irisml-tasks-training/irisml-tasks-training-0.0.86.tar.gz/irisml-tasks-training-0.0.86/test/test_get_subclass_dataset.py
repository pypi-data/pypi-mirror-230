import unittest
import torch
from irisml.tasks.get_subclass_dataset import Task


class TestSubClasstDataset(unittest.TestCase):
    def test_ic_multiclass(self):
        num_classes = 10
        dataset = [(None, torch.tensor(i % num_classes)) for i in range(50)]
        class_names = [str(i) for i in range(num_classes)]

        for class_id in range(num_classes):
            outputs = Task(Task.Config([class_id])).execute(Task.Inputs(dataset, class_names))
            self.assertEqual(len(outputs.dataset), 5)
            self.assertEqual(outputs.num_classes, 1)
            self.assertCountEqual(outputs.class_names, [str(class_id)])
            classes = set(int(t) for _, t in outputs.dataset)
            self.assertSetEqual(classes, {class_id})

        outputs = Task(Task.Config([0, 1])).execute(Task.Inputs(dataset, class_names))
        self.assertEqual(outputs.class_names, ['0', '1'])
        self.assertEqual(len(outputs.dataset), 10)
        self.assertEqual(outputs.num_classes, 2)

        with self.assertRaises(ValueError):
            outputs = Task(Task.Config([0, 12])).execute(Task.Inputs(dataset, class_names))

        with self.assertRaises(ValueError):
            outputs = Task(Task.Config([10])).execute(Task.Inputs(dataset, class_names))

    def test_od(self):
        dataset = [(None, torch.tensor([[0, 0, 0, 0.5, 0.5], [1, 0.5, 0.5, 1, 1]])), (None, torch.tensor([[1, 0, 0, 0.2, 0.2], [1, 0.2, 0.2, 0.4, 0.4]])), (None, torch.tensor([[0, 0, 0, 1, 1]]))]
        class_names = ['0', '1']
        outputs = Task(Task.Config([0])).execute(Task.Inputs(dataset, class_names))
        self.assertEqual(len(outputs.dataset), 2)
        self.assertCountEqual(outputs.class_names, ['0'])
        self.assertEqual(outputs.num_classes, 1)

        outputs = Task(Task.Config([1])).execute(Task.Inputs(dataset, class_names))
        self.assertEqual(len(outputs.dataset), 2)
        self.assertCountEqual(outputs.class_names, ['1'])

        with self.assertRaises(ValueError):
            outputs = Task(Task.Config([3, 0])).execute(Task.Inputs(dataset, class_names))

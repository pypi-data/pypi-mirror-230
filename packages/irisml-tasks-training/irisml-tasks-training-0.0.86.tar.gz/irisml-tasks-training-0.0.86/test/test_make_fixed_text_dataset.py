import unittest
from irisml.tasks.make_fixed_text_dataset import Task


class TestMakeFixedTextDataset(unittest.TestCase):
    def test_simple(self):
        texts = ['str1', 'str2', 'str3']
        outputs = Task(Task.Config()).execute(Task.Inputs(texts))
        dataset = outputs.dataset

        self.assertEqual(len(dataset), 3)
        self.assertEqual(dataset[0], (('str1', []), None))
        self.assertEqual(dataset[1], (('str2', []), None))
        self.assertEqual(dataset[2], (('str3', []), None))

import unittest
import PIL.Image
import torch.utils.data
from irisml.tasks.get_questions_from_vqa_dataset import Task


class FakeDataset(torch.utils.data.Dataset):
    def __init__(self, data):
        self._data = data

    def __getitem__(self, index):
        return self._data[index]

    def __len__(self):
        return len(self._data)


class TestGetQuestionsFromVqaDataset(unittest.TestCase):
    def test_simple(self):
        data = [((PIL.Image.new('RGB', (224, 224)), 'What is this?'), 'Apple'),
                ((PIL.Image.new('RGB', (224, 224)), 'Where is it?'), 'Paris')]

        dataset = FakeDataset(data)

        outputs = Task(Task.Config()).execute(Task.Inputs(dataset))
        self.assertEqual(outputs.questions, ['What is this?', 'Where is it?'])

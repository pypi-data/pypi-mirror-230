import unittest
import torch
from irisml.tasks.find_incorrect_classification_multilabel_indices import Task


class TestFindIncorrectClassificationMultilabelIndices(unittest.TestCase):
    def test_simple(self):
        predictions_list = [torch.tensor([0, 1, 2]), torch.tensor([0, 1, 2])]
        targets_list = [torch.tensor([0, 1, 2]), torch.tensor([0, 1, 2])]
        outputs = Task(Task.Config()).execute(Task.Inputs(predictions_list=predictions_list, targets_list=targets_list))
        self.assertEqual(len(outputs.indices), 0)

        predictions_list = [torch.tensor([0, 1, 2]), torch.tensor([0, 1, 2])]
        targets_list = [torch.tensor([0, 1, 2]), torch.tensor([0, 1, 3])]
        outputs = Task(Task.Config()).execute(Task.Inputs(predictions_list=predictions_list, targets_list=targets_list))
        self.assertEqual(outputs.indices.tolist(), [1])

        targets = torch.tensor([0, 1])
        outputs = Task(Task.Config()).execute(Task.Inputs(predictions_list=predictions_list, targets=targets))
        self.assertEqual(outputs.indices.tolist(), [0, 1])

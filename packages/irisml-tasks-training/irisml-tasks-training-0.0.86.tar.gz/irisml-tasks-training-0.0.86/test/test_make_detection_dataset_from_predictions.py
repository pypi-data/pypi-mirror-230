import unittest
import unittest.mock
import PIL.Image
import torch
from irisml.tasks.make_detection_dataset_from_predictions import Task
from utils import FakeDataset


class TestMakeClassificationDatasetFromObjectDetection(unittest.TestCase):
    def build_dataset(self):
        fake_image = PIL.Image.new('RGB', (10, 10))
        dataset = FakeDataset([(fake_image, torch.tensor([[0, 0, 0, 0.5, 0.5], [1, 0, 0, 0.1, 0.1]])),
                               (fake_image, torch.zeros(0, 5)),
                               (fake_image, torch.tensor([[2, 0, 0, 0.5, 0.5], [3, 0, 0, 0.1, 0.1]]))])
        return dataset

    def test_simple(self):
        dataset = self.build_dataset()

        predictions_xyxy = [torch.tensor([[0, 0.1, 0.1, 0.4, 0.5], [1, 0.1, 0.1, 0.2, 0.2]]), torch.empty(0, 5), torch.tensor([[2, 0, 0, 1, 1]])]
        outputs = Task(Task.Config()).execute(Task.Inputs(dataset, predictions_xyxy))

        self.assertEqual(len(outputs.dataset), 3)
        for im, _ in outputs.dataset:
            self.assertEqual(im.size, (10, 10))

        # Test normalized coordinates.
        self.assertTrue(torch.equal(outputs.dataset[0][1], torch.tensor([[0, 0.1, 0.1, 0.4, 0.5], [1, 0.1, 0.1, 0.2, 0.2]])))
        self.assertTrue(torch.equal(outputs.dataset[1][1], torch.empty(0, 5)))
        self.assertTrue(torch.equal(outputs.dataset[2][1], torch.tensor([[2, 0, 0, 1, 1]])))

    def test_normalize(self):
        dataset = self.build_dataset()
        predictions_absolute = [torch.tensor([[0, 1, 1, 4, 5], [1, 1, 1, 2, 2]]), torch.empty(0, 5), torch.tensor([[2, 0, 0, 10, 10]])]
        outputs = Task(Task.Config(normalized=False)).execute(Task.Inputs(dataset, predictions_absolute))
        self.assertTrue(torch.equal(outputs.dataset[0][1], torch.tensor([[0, 0.1, 0.1, 0.4, 0.5], [1, 0.1, 0.1, 0.2, 0.2]])))
        self.assertTrue(torch.equal(outputs.dataset[1][1], torch.empty(0, 5)))
        self.assertTrue(torch.equal(outputs.dataset[2][1], torch.tensor([[2, 0, 0, 1, 1]])))

    def test_invalid_coordinates(self):
        dataset = self.build_dataset()
        # Some coordindates are not within [0, 1].
        predictions_xyxy_invalid = [torch.tensor([[0, 0.1, 0.1, 1.1, 0.5], [1, 0.1, 0.1, 0.2, 0.2]]), torch.empty(0, 5), torch.tensor([[2, -0.2, 0, 1.5, 1.2]])]
        outputs = Task(Task.Config()).execute(Task.Inputs(dataset, predictions_xyxy_invalid))
        self.assertTrue(torch.equal(outputs.dataset[0][1], torch.tensor([[0, 0.1, 0.1, 1.0, 0.5], [1, 0.1, 0.1, 0.2, 0.2]])))
        self.assertTrue(torch.equal(outputs.dataset[1][1], torch.empty(0, 5)))
        self.assertTrue(torch.equal(outputs.dataset[2][1], torch.tensor([[2, 0, 0, 1, 1]])))

    def test_predictions_with_score(self):
        dataset = self.build_dataset()
        predictions_with_scores = [torch.tensor([[0, 0.8, 0.1, 0.1, 0.9, 0.5], [1, 0.3, 0.1, 0.1, 0.2, 0.2]]), torch.empty(0, 6), torch.tensor([[2, 0.2, 0.2, 0, 1.5, 1.2]])]
        outputs = Task(Task.Config(score_threshold=0.5)).execute(Task.Inputs(dataset, predictions_with_scores))
        self.assertTrue(torch.equal(outputs.dataset[0][1], torch.tensor([[0, 0.1, 0.1, 0.9, 0.5]])))
        self.assertTrue(torch.equal(outputs.dataset[1][1], torch.empty(0, 5)))
        self.assertTrue(torch.equal(outputs.dataset[2][1], torch.empty(0, 5)))

    def test_predictions_with_score_xywh(self):
        dataset = self.build_dataset()
        predictions_with_scores = [torch.tensor([[0, 0.8, 0.1, 0.1, 0.5, 0.6], [1, 0.3, 0.1, 0.1, 0.3, 0.3]]), torch.empty(0, 6), torch.tensor([[2, 0.2, 0, 0, 1, 1]])]
        outputs = Task(Task.Config(score_threshold=0.5)).execute(Task.Inputs(dataset, predictions_with_scores))
        self.assertTrue(torch.equal(outputs.dataset[0][1], torch.tensor([[0, 0.1, 0.1, 0.5, 0.6]])))
        self.assertTrue(torch.equal(outputs.dataset[1][1], torch.empty(0, 5)))
        self.assertTrue(torch.equal(outputs.dataset[2][1], torch.empty(0, 5)))

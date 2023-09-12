import unittest
import unittest.mock
import torch
from irisml.tasks.map_classification_predictions_to_detection import Task


class TestMapClassificationPredictionsToDetection(unittest.TestCase):
    def create_detections_and_index_mappings(self):
        detections = [torch.tensor([[0, 0, 0, 0.5, 0.5], [1, 0, 0, 0.1, 0.1]]), torch.empty(0, 5), torch.tensor([[2, 0, 0, 0.5, 0.5], [3, 0, 0, 0.1, 0.1]])]
        index_mappings = [(0, 0), (0, 1), (2, 0), (2, 1)]
        return detections, index_mappings

    def create_detections_with_score_and_index_mappings(self):
        detections = [torch.tensor([[0, 0.1, 0, 0, 0.5, 0.5], [1, 0.1, 0, 0, 0.1, 0.1]]), torch.empty(0, 5), torch.tensor([[2, 0.8, 0, 0, 0.5, 0.5], [3, 0.8, 0, 0, 0.1, 0.1]])]
        index_mappings = [(0, 0), (0, 1), (2, 0), (2, 1)]
        return detections, index_mappings

    def test_simple(self):
        detections, index_mappings = self.create_detections_with_score_and_index_mappings()
        classifications = torch.tensor([5, 5, 10, 10])
        outputs = Task(Task.Config(score_type='od')).execute(Task.Inputs(classifications, detections, index_mappings))
        self.assertTrue(torch.equal(outputs.detection_predictions[0], torch.tensor([[5, 0.1, 0, 0, 0.5, 0.5], [5, 0.1, 0, 0, 0.1, 0.1]])))
        self.assertTrue(torch.equal(outputs.detection_predictions[1], torch.empty(0, 6)))
        self.assertTrue(torch.equal(outputs.detection_predictions[2], torch.tensor([[10, 0.8, 0, 0, 0.5, 0.5], [10, 0.8, 0, 0, 0.1, 0.1]])))

    def test_ic_probability(self):
        detections, index_mappings = self.create_detections_and_index_mappings()
        classifications = torch.tensor([[0.9, 0.1], [0.8, 0.2], [0.2, 0.8], [0.1, 0.9]])
        outputs = Task(Task.Config(score_type='ic')).execute(Task.Inputs(classifications, detections, index_mappings))
        self.assertTrue(torch.equal(outputs.detection_predictions[0], torch.tensor([[0, 0.9, 0, 0, 0.5, 0.5], [0, 0.8, 0, 0, 0.1, 0.1]])))
        self.assertTrue(torch.equal(outputs.detection_predictions[1], torch.empty(0, 6)))
        self.assertTrue(torch.equal(outputs.detection_predictions[2], torch.tensor([[1, 0.8, 0, 0, 0.5, 0.5], [1, 0.9, 0, 0, 0.1, 0.1]])))

    def test_prod_avg_score(self):
        detections, index_mappings = self.create_detections_with_score_and_index_mappings()
        classifications = torch.tensor([[0.9, 0.1], [0.8, 0.2], [0.2, 0.8], [0.1, 0.9]])
        outputs = Task(Task.Config(score_type='prod')).execute(Task.Inputs(classifications, detections, index_mappings))
        self.assertTrue(torch.allclose(outputs.detection_predictions[0], torch.tensor([[0, 0.09, 0, 0, 0.5, 0.5], [0, 0.08, 0, 0, 0.1, 0.1]])))
        self.assertTrue(torch.equal(outputs.detection_predictions[1], torch.empty(0, 6)))
        self.assertTrue(torch.allclose(outputs.detection_predictions[2], torch.tensor([[1, 0.64, 0, 0, 0.5, 0.5], [1, 0.72, 0, 0, 0.1, 0.1]])))

        outputs = Task(Task.Config(score_type='avg')).execute(Task.Inputs(classifications, detections, index_mappings))
        self.assertTrue(torch.allclose(outputs.detection_predictions[0], torch.tensor([[0, 0.5, 0, 0, 0.5, 0.5], [0, 0.45, 0, 0, 0.1, 0.1]])))
        self.assertTrue(torch.equal(outputs.detection_predictions[1], torch.empty(0, 6)))
        self.assertTrue(torch.allclose(outputs.detection_predictions[2], torch.tensor([[1, 0.8, 0, 0, 0.5, 0.5], [1, 0.85, 0, 0, 0.1, 0.1]])))

    def test_invalid_inputs(self):
        detections, index_mappings = self.create_detections_and_index_mappings()
        index_mappings_shorter = index_mappings[:-1]
        classifications = torch.tensor([[0.9, 0.1], [0.8, 0.2], [0.2, 0.8], [0.1, 0.9]])
        with self.assertRaisesRegex(ValueError, "IC predictions have different samples from the IC to OD index mapping: 4 vs 3"):
            Task(Task.Config()).execute(Task.Inputs(classifications, detections, index_mappings_shorter))

        with self.assertRaisesRegex(ValueError, "When OD scores not provided, score_type has to be ic and IC scores have to be provided!"):
            Task(Task.Config(score_type='od')).execute(Task.Inputs(classifications, detections, index_mappings))

        classifications_no_score = torch.tensor([5, 5, 10, 10])
        detections, index_mappings = self.create_detections_with_score_and_index_mappings()
        with self.assertRaisesRegex(ValueError, "When IC scores not provided, score_type has to be od and OD scores have to be provided!"):
            Task(Task.Config(score_type='ic')).execute(Task.Inputs(classifications_no_score, detections, index_mappings))

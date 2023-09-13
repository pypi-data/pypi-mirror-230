import unittest
import PIL.Image
import torch
import torchvision.transforms
from irisml.tasks.make_vqa_image_transform import Task


class TestMakeVqaImageTransform(unittest.TestCase):
    def test_simple(self):
        image_transform = torchvision.transforms.ToTensor()

        outputs = Task(Task.Config()).execute(Task.Inputs(image_transform))
        transform = outputs.transform

        transform_outputs = transform((PIL.Image.new('RGB', (32, 32)), 'What is this?'), 'R2D2')
        self.assertEqual(transform_outputs[0][0], '<|image|> question: What is this? answer:')
        self.assertIsInstance(transform_outputs[0][1], torch.Tensor)
        self.assertEqual(transform_outputs[1], 'R2D2')

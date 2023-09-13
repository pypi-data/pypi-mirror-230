import unittest
import PIL.Image
import torch
import torchvision
from irisml.tasks.make_prompt_list_image_transform import Task


class TestMakePromptListImageTransform(unittest.TestCase):
    def test_simple(self):
        image_transform = torchvision.transforms.ToTensor()
        prompts = ['prompt1', 'prompt2']
        outputs = Task(Task.Config()).execute(Task.Inputs(image_transform, prompts))
        transform = outputs.transform

        self.assertEqual(transform(PIL.Image.new('RGB', (1, 1)), torch.tensor(0))[0][0], 'prompt1')
        self.assertEqual(transform(PIL.Image.new('RGB', (1, 1)), torch.tensor(1))[0][0], 'prompt2')
        self.assertTrue(torch.equal(transform(PIL.Image.new('RGB', (1, 1)), torch.tensor(0))[0][1][0], torch.zeros(3, 1, 1)))
        self.assertTrue(torch.equal(transform(PIL.Image.new('RGB', (1, 1)), torch.tensor(0))[0][1][0], torch.zeros(3, 1, 1)))
        self.assertTrue(torch.equal(transform(PIL.Image.new('RGB', (1, 1)), torch.tensor(1))[1], torch.tensor(1)))

import dataclasses
from typing import Callable, Tuple
import PIL.Image
import torch
import irisml.core


class Task(irisml.core.TaskBase):
    """Creates a transform function for VQA task.

    The transform function expects two arguments: inputs and targets. inputs is a tuple of (image, question), where
    image is a PIL image and question is a string. targets is a string. The transform function returns ((prompt, image_tensor), targets),
    where prompt is a string and image_tensor is a torch tensor
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        image_transform: Callable[[PIL.Image.Image], torch.Tensor]

    @dataclasses.dataclass
    class Outputs:
        transform: Callable[[Tuple[PIL.Image.Image, str], str], Tuple[Tuple[str, torch.Tensor], str]]

    def execute(self, inputs):
        transform = VqaImageTransform(inputs.image_transform)
        return self.Outputs(transform=transform)

    def dry_run(self, inputs):
        return self.execute(inputs)


class VqaImageTransform:
    def __init__(self, image_transform):
        self._image_transform = image_transform

    def __call__(self, inputs, targets):
        image, question = inputs
        assert isinstance(image, PIL.Image.Image)
        image_tensor = self._image_transform(image)
        prompt = f'<|image|> question: {question} answer:'
        return (prompt, image_tensor), targets

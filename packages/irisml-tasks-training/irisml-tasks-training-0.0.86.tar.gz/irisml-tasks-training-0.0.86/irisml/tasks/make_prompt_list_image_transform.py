import dataclasses
import typing
import PIL.Image
import torch
import irisml.core


class Task(irisml.core.TaskBase):
    """Make a transform function for image and prompt list.

    The interface of the transform function is:
    - Input: (PIL.Image.Image, torch.Tensor), where the tensor is a scalar index of the prompt list.
    - Output: (str, [torch.Tensor]), where the string is the prompt, and the list of tensors is the image.
    """

    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        image_transform: typing.Callable
        prompts: typing.List[str]

    @dataclasses.dataclass
    class Outputs:
        transform: typing.Callable

    def execute(self, inputs):
        return self.Outputs(PromptListImageTransform(inputs.image_transform, inputs.prompts))

    def dry_run(self, inputs):
        return self.execute(inputs)


class PromptListImageTransform:
    def __init__(self, image_transform, prompts):
        self._image_transform = image_transform
        self._prompts = prompts

    def __call__(self, inputs, targets):
        assert isinstance(inputs, PIL.Image.Image)
        image_tensor = self._image_transform(inputs)
        assert isinstance(image_tensor, torch.Tensor)
        assert isinstance(targets, torch.Tensor) and targets.dim() == 0, f"targets: {targets}"
        prompt = self._prompts[targets.item()]
        return (prompt, [image_tensor]), targets

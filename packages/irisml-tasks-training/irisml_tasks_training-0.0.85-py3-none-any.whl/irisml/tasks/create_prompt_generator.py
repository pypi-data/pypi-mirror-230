import dataclasses
import typing
import irisml.core


class Task(irisml.core.TaskBase):
    """Create a prompt generator that returns a list of prompts for a given label.

    Config:
        templates (List[str]): List of templates to use for the generator. Each template must contain a single {}.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Config:
        templates: typing.List[str]

    @dataclasses.dataclass
    class Outputs:
        generator: typing.Callable[[str], typing.List[str]]

    def execute(self, inputs):
        if not self.config.templates:
            raise ValueError('Templates must be provided.')
        return self.Outputs(PromptGenerator(self.config.templates))

    def dry_run(self, inputs):
        return self.execute(inputs)


class PromptGenerator:
    def __init__(self, templates):
        self._templates = templates

    def __call__(self, label_name: str) -> typing.List[str]:
        return [t.format(label_name) for t in self._templates]

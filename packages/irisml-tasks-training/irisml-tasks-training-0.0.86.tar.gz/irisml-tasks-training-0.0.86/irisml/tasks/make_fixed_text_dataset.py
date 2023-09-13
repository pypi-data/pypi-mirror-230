import dataclasses
import logging
import typing
import torch.utils.data
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Create a dataset with a list of strings.

    This dataset returns a tuple of ((text, []), None) for each item.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        texts: typing.List[str]

    @dataclasses.dataclass
    class Outputs:
        dataset: torch.utils.data.Dataset

    def execute(self, inputs):
        logger.info(f"Creating a fixed text dataset with {len(inputs.texts)} texts")
        dataset = FixedTextDataset(inputs.texts)
        return self.Outputs(dataset=dataset)

    def dry_run(self, inputs):
        return self.execute(inputs)


class FixedTextDataset(torch.utils.data.Dataset):
    def __init__(self, texts):
        super().__init__()
        self._texts = texts

    def __len__(self):
        return len(self._texts)

    def __getitem__(self, index):
        return (self._texts[index], []), None

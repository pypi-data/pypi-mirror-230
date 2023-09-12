import typing
import dataclasses
import logging
import torch.utils.data

import irisml.core
from irisml.tasks.sample_few_shot_dataset import _get_class_id_set

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Get the sub-dataset with given class ids from a dataset."""
    VERSION = '0.0.1'

    @dataclasses.dataclass
    class Config:
        class_ids: typing.List[int]

    @dataclasses.dataclass
    class Inputs:
        dataset: torch.utils.data.Dataset
        class_names: typing.List[str]

    @dataclasses.dataclass
    class Outputs:
        dataset: torch.utils.data.Dataset
        class_names: typing.List[str]
        num_classes: int

    def execute(self, inputs):
        class_ids = sorted(self.config.class_ids)
        subclass_dataset = SubClassDataset(inputs.dataset, class_ids)
        subclass_names = [inputs.class_names[i] for i in class_ids]
        return Task.Outputs(subclass_dataset, subclass_names, len(subclass_names))

    def dry_run(self, inputs):
        return self.execute(inputs)


class SubClassDataset(torch.utils.data.Dataset):
    def __init__(self, dataset, class_ids):
        super().__init__()
        self._dataset = dataset
        subclasses = set(class_ids)

        classes_by_images = []
        for i in range(len(dataset)):
            target = dataset.get_targets(i) if hasattr(dataset, 'get_targets') else dataset[i][1]
            classes_by_images.append(_get_class_id_set(target))
        classes = set.union(*classes_by_images)

        if not subclasses.issubset(classes):
            raise ValueError(f"Given sub-class ids {subclasses} are not a subset of dataset class ids: {classes}.")
        self._id_mappings = [i for i in range(len(dataset)) if classes_by_images[i].intersection(subclasses)]
        logger.info(f"Extracted subset with {len(self._id_mappings)} images of given class ids: {class_ids}.")

    def __len__(self):
        return len(self._id_mappings)

    def __getitem__(self, index):
        new_id = self._id_mappings[index]
        assert isinstance(new_id, int)
        return self._dataset[new_id]

    def get_targets(self, index):
        return self._dataset.get_targets(self._id_mappings[index])

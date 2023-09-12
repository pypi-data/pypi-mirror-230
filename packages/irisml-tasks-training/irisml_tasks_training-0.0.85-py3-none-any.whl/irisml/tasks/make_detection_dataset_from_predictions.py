import dataclasses
import typing
import torch
import irisml.core


class DatasetWithTargets(torch.utils.data.Dataset):
    def __init__(self, dataset, targets):
        super().__init__()
        self._dataset = dataset
        self._targets = targets

    def __len__(self):
        return len(self._dataset)

    def __getitem__(self, index):
        return self._dataset[index][0], self._targets[index]

    def get_targets(self, index):
        return self._targets[index]


class Task(irisml.core.TaskBase):
    """Make a detection dataset from predictions.

    This task takes a OD dataset and a list of tensor predictions or targets and returns a new dataset
    with the targets set to the provided targets.

    The predictions is a list of tensors, each tensor contains predictions for an image, with shape (N, 5) (targets) or (N, 6) (predictions), each row is class (,score), and box coordinates.

    Output targets bounding boxes will be in xyxy normalized format.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        dataset: torch.utils.data.Dataset
        predictions: typing.List[torch.Tensor]

    @dataclasses.dataclass
    class Config:
        normalized: bool = True
        score_threshold: float = 0.

    @dataclasses.dataclass
    class Outputs:
        dataset: torch.utils.data.Dataset
        predictions: typing.List[torch.Tensor]

    def execute(self, inputs):
        predictions = [torch.as_tensor(p) for p in inputs.predictions]
        predictions = [p[p[:, 1] > self.config.score_threshold] for p in predictions] if predictions[0].shape[1] == 6 else predictions

        if len(inputs.dataset) != len(predictions):
            raise ValueError(f"Dataset and predictions have different lengths: {len(inputs.dataset)} vs {len(predictions)}")

        # Normalized box coordinates.
        if not self.config.normalized:
            for i in range(len(inputs.dataset)):
                if predictions[i].nelement():
                    img = inputs.dataset[i][0]
                    w, h = img.size
                    predictions[i] = predictions[i].float()
                    predictions[i][:, -4] /= w
                    predictions[i][:, -3] /= h
                    predictions[i][:, -2] /= w
                    predictions[i][:, -1] /= h

        predictions = self._correct_coordinates(predictions)
        targets = [torch.cat((p[:, :1], p[:, 2:]), dim=1) for p in predictions] if predictions[0].shape[1] == 6 else predictions

        return self.Outputs(dataset=DatasetWithTargets(inputs.dataset, targets), predictions=predictions)

    def _correct_coordinates(self, targets):
        # Make coordinates within [0, 1].
        return [torch.cat((t[:, :1], torch.clamp(t[:, 1:], min=0., max=1.)), dim=1) for t in targets]

    def dry_run(self, inputs):
        return self.execute(inputs)

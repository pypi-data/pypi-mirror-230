import dataclasses
import logging
from typing import List, Optional
import torch
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Find incorrect classification indices for multilabel classification.

    Inputs:
        predictions_list (List[LongTensor]): List of predicted indices. Each element must be 1D.
        targets (Tensor): 1D tensor of target indices. Either targets or targets_list must be provided.
        targets_list (List[Tensor]): List of target indices. Each element must be 1D.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        # predictions: Optional[torch.Tensor] = None # NYI
        predictions_list: List[torch.Tensor]
        targets: Optional[torch.Tensor] = None
        targets_list: Optional[List[torch.Tensor]] = None

    @dataclasses.dataclass
    class Outputs:
        indices: torch.Tensor

    def execute(self, inputs):
        if inputs.targets is None and inputs.targets_list is None:
            raise ValueError("targets or targets_list must be provided")
        if inputs.targets is not None and inputs.targets_list is not None:
            raise ValueError("only one of targets or targets_list must be provided")

        if any(torch.is_floating_point(prediction) for prediction in inputs.predictions_list):
            raise ValueError("predictions_list must not be float.")

        predictions_list = inputs.predictions_list
        targets_list = inputs.targets_list
        if targets_list is None:
            targets_list = [t.reshape(1) for t in inputs.targets]

        if len(predictions_list) != len(targets_list):
            raise ValueError("The number of predictions and targets must be the same.")

        indices = []
        for i in range(len(predictions_list)):
            if set(predictions_list[i].tolist()) != set(targets_list[i].tolist()):
                logger.info(f"Index {i}: Predicted: {predictions_list[i].tolist()}, Actual: {targets_list[i].tolist()}")
                indices.append(i)

        return self.Outputs(torch.tensor(indices, dtype=torch.int64))

    def dry_run(self, inputs):
        return self.execute(inputs)

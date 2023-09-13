import dataclasses
import typing
import torch
import irisml.core


class Task(irisml.core.TaskBase):
    """Map classification predictions back to detection predictions or targets.

    This tasks is to apply the second-stage IC model predictions back to the OD data. It takes IC prediction (images cropped from OD dataset), OD predictions or targets,
    and the index mapping as input, outputs detection predictions with scores, where the score can be IC score, OD score, product or average.

    The detection prediction classes will always be replaced by classification.

    Inputs:
        classifications: tensor of shape (N, C) where C is num of classes, with the predicted probabilities; or (N,) with the predicted classes only
        detections: a list of tensors with (N_i, 6) with scores or (N_i, 5) without scores, where N_i is num of boxes for image i
        index_mappings: IC image index to a tuple (original image index in OD dataset, box index in that image)

    Outputs:
        detection_predictions: a list of tensors with (N_i, 6) with scores, where N_i is num of boxes for image i
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        classifications: torch.Tensor
        detections: typing.List[torch.Tensor]
        index_mappings: typing.List[typing.Tuple[int, int]]

    @dataclasses.dataclass
    class Config:
        score_type: typing.Literal['ic', 'od', 'prod', 'avg'] = 'ic'

    @dataclasses.dataclass
    class Outputs:
        detection_predictions: typing.List[torch.Tensor]

    def execute(self, inputs):
        detections = [torch.as_tensor(d) for d in inputs.detections]
        if inputs.classifications.shape[0] != len(inputs.index_mappings):
            raise ValueError(f"IC predictions have different samples from the IC to OD index mapping: {inputs.classifications.shape[0]} vs {len(inputs.index_mappings)}")
        if detections[0].shape[1] == 5 and (self.config.score_type != 'ic' or inputs.classifications.ndim == 1):
            raise ValueError("When OD scores not provided, score_type has to be ic and IC scores have to be provided!")
        if inputs.classifications.ndim == 1 and (self.config.score_type != 'od' or detections[0].shape[1] == 5):
            raise ValueError("When IC scores not provided, score_type has to be od and OD scores have to be provided!")
        if self.config.score_type not in ['ic', 'od', 'prod', 'avg']:
            raise ValueError(f"score type must be one of 'ic', 'od', 'prod', 'avg', got {self.config.score_type}")

        if inputs.classifications.ndim == 2:
            ic_scores, ic_pred_classes = torch.max(inputs.classifications, dim=-1)
        else:  # if no IC scores are provided
            ic_pred_classes = inputs.classifications
            ic_scores = torch.ones_like(ic_pred_classes, dtype=float)

        output = [torch.zeros((img_detections.shape[0], 6)) for img_detections in detections]
        for ic_pred_class, ic_score, (img_id, box_id_in_img) in zip(ic_pred_classes, ic_scores, inputs.index_mappings):
            if self.config.score_type == 'ic':
                score = ic_score
            else:
                od_score = detections[img_id][box_id_in_img][1]
                if self.config.score_type == 'od':
                    score = od_score
                elif self.config.score_type == 'prod':
                    score = ic_score * od_score
                else:
                    score = (ic_score + od_score) * 0.5
            output[img_id][box_id_in_img][:2] = torch.tensor([ic_pred_class, score])
            output[img_id][box_id_in_img][2:] = detections[img_id][box_id_in_img][-4:]

        return self.Outputs(output)

    def dry_run(self, inputs):
        return self.execute(inputs)

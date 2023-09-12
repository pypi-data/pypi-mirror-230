import dataclasses
import json
import logging
import typing
import pathlib
import torch
import torch.utils.data
from torchvision.transforms import ToPILImage
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Export coco dataset from a given torch dataset. Support IC and OD only.

    For IC dataset, target is either 0 or 1 dim array; for OD, target is 2-dim array with each row being [label, x1, y1, x2, y2] normalized.
    The images are saved to [dirpath]/[image_directory_name]/[image_id].[image_extension].

    In the COCO file, the file_name for each image is relative to dirpath, bbox coordinates are [x, y, w, h] absolute.
    """
    VERSION = '0.1.0'
    CACHE_ENABLED = False

    @dataclasses.dataclass
    class Inputs:
        dataset: torch.utils.data.Dataset
        class_names: typing.List[str]

    @dataclasses.dataclass
    class Config:
        task_type: typing.Literal['classification_multiclass', 'classification_multilabel', 'object_detection']
        dirpath: pathlib.Path = pathlib.Path('.')
        image_directory_name: str = 'images'
        json_file_name: str = 'images'
        image_extension: typing.Literal['png', 'jpg'] = 'png'

    def execute(self, inputs):
        def _convert_bbox(bbox: list, w: int, h: int):
            return [bbox[0] * w, bbox[1] * h, (bbox[2] - bbox[0]) * w, (bbox[3] - bbox[1]) * h]

        if (self.config.dirpath / f'{self.config.json_file_name}.json').exists():
            raise RuntimeError(f'{self.config.json_file_name}.json already exists in {self.config.dirpath}!')

        image_dir = self.config.dirpath / self.config.image_directory_name
        image_dir.mkdir(parents=True, exist_ok=True)
        dataset = inputs.dataset

        coco = {"images": [], "annotations": []}
        coco["categories"] = [{"id": i + 1, "name": inputs.class_names[i]} for i in range(len(inputs.class_names))]
        anno_idx = 1
        tensor_to_pil = ToPILImage()

        for image_id, (image, targets) in enumerate(dataset, 1):
            image_path = image_dir / f"{image_id}.{self.config.image_extension}"
            if isinstance(image, torch.Tensor):
                image = tensor_to_pil(image)
            image.save(image_path)
            logger.info(f"Index {image_id - 1} image saved to {str(image_path)}.")

            w, h = image.size
            image_info = {"id": image_id, "width": w, "height": h, "file_name": f"{self.config.image_directory_name}/{image_path.name}"}
            coco["images"].append(image_info)

            if not isinstance(targets, torch.Tensor):
                targets = torch.tensor(targets)

            if self.config.task_type == 'classification_multiclass':
                annos = [{"id": anno_idx, "category_id": int(targets if targets.dim() == 0 else targets[0]) + 1, "image_id": image_id}]
            elif self.config.task_type == 'classification_multilabel':
                annos = [{"id": anno_idx + i, "category_id": int(t) + 1, "image_id": image_id} for i, t in enumerate(targets)]
            else:
                annos = [{"id": anno_idx + i, "category_id": int(t[0]) + 1, "image_id": image_id, "bbox": _convert_bbox(t[1:].tolist(), w, h)} for i, t in enumerate(targets)]

            coco['annotations'].extend(annos)
            anno_idx += len(annos)

        (self.config.dirpath / f"{self.config.json_file_name}.json").write_text(json.dumps(coco, indent=2))
        return self.Outputs()

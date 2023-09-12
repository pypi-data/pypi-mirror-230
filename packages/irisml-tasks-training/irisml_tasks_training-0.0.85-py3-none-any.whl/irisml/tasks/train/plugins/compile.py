"""Compile the model module using torch.compile."""
import logging
import torch
from .plugin_base import PluginBase

logger = logging.getLogger(__name__)


class Plugin(PluginBase):
    def on_train_start(self, trainer, model):
        logger.info("Compiling the model module.")
        self._original_model = model
        return torch.compile(model)

    def on_train_end(self, trainer, model):
        # The OptimizedModule shares the same state_dict with the original model.
        model = self._original_model
        del self._original_model
        return model

    def on_prediction_start(self, trainer, model):
        return self.on_train_start(trainer, model)

    def on_prediction_end(self, trainer, model):
        return self.on_train_end(trainer, model)

import dataclasses
import itertools
import logging
import math
import multiprocessing
import os
import typing
import torch.utils.data
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Extracts questions from a VQA dataset.

    __getitem__() of the dataset must return a tuple of ((image, question), answer), where image is a PIL image,
    question is a string, and answer is a string.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        dataset: torch.utils.data.Dataset

    @dataclasses.dataclass
    class Outputs:
        questions: typing.List[str]

    def execute(self, inputs):
        num_processes = len(os.sched_getaffinity(0))
        assert num_processes > 0
        batch_size = math.ceil(len(inputs.dataset) / num_processes)

        logger.info(f"Using {num_processes} processes to collect {len(inputs.dataset)} questions.")

        context = multiprocessing.get_context('fork')
        queue = context.JoinableQueue(num_processes)
        processes = [context.Process(target=Task._worker, args=(inputs.dataset, i, batch_size, queue), daemon=True) for i in range(num_processes)]
        for p in processes:
            p.start()

        collected_batches = [None] * num_processes
        for _ in range(num_processes):
            i, batch = queue.get(timeout=3600)
            collected_batches[i] = batch
            queue.task_done()

        for p in processes:
            p.join()

        assert all(b is not None for b in collected_batches)
        questions = list(itertools.chain.from_iterable(collected_batches))
        logger.info(f"Collected {len(questions)} questions.")
        assert len(questions) == len(inputs.dataset)

        return self.Outputs(questions)

    @staticmethod
    def _worker(dataset, process_index, batch_size, queue):
        start_index = batch_size * process_index
        end_index = min(start_index + batch_size, len(dataset))
        questions = [dataset[i][0][1] for i in range(start_index, end_index)]
        queue.put((process_index, questions))
        queue.join()

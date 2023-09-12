import unittest
from irisml.tasks.create_prompt_generator import Task


class TestCreatePromptGenerator(unittest.TestCase):
    def test_simple(self):
        outputs = Task(Task.Config(templates=['a photo of a {}'])).execute(Task.Inputs())
        self.assertEqual(outputs.generator('cat'), ['a photo of a cat'])

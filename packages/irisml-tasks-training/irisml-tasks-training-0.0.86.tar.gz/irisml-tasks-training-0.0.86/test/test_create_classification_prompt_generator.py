import unittest
from irisml.tasks.create_classification_prompt_generator import Task


class TestCreateClassificationPromptGenerator(unittest.TestCase):
    def test_simple(self):
        outputs = Task(Task.Config()).execute(Task.Inputs())

        results = outputs.generator('random_string')
        self.assertGreater(len(results), 1)
        self.assertTrue(all('random_string' in r for r in results))

    def test_template(self):
        outputs = Task(Task.Config(name='template', template='This is an image of {}')).execute(Task.Inputs())

        self.assertEqual(outputs.generator('label_name'), ['This is an image of label_name'])

        # No template
        outputs = Task(Task.Config(name='template')).execute(Task.Inputs())

        self.assertEqual(outputs.generator('label_name'), ['label_name'])

        # Without {} in the template
        with self.assertRaises(ValueError):
            Task(Task.Config(name='template', template='This is an image of')).execute(Task.Inputs())

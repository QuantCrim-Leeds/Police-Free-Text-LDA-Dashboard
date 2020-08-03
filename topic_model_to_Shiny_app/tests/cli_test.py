import os
import unittest
from unittest.mock import patch
import pkg_resources
from click.testing import CliRunner
from topic_model_to_Shiny_app.topic2shiny import main

resource_package = 'topic_model_to_Shiny_app'

test_dir = os.path.dirname(os.path.abspath(__file__))

class CLI_test(unittest.TestCase):

    def test_CLI(self):
        # these are examples and will fail
        # TODO: update these to actually test CLI
        runner = CliRunner()
        result = runner.invoke(main, 
                               ['--input-data', str(pkg_resources.resource_filename(resource_package, 'tests/test_data/test_data.csv')),
                                '--output-dir', str(os.path.join(test_dir,'test_output')),
                                '--num-runs', '3',
                                '--pretrained', 'False',
                                '--shiny-start', 'False'])
        print(result)
        self.assertEqual(result.exit_code, 0)


    def test_CLI_fail(self):

        return


if __name__ == "__main__":

    unittest.main(verbosity=2)

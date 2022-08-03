import os
import unittest
from unittest.mock import patch
import pkg_resources
from click.testing import CliRunner
from topic_model_to_Shiny_app.topic2shiny import main

resource_package = 'topic_model_to_Shiny_app'

test_dir = os.path.dirname(os.path.abspath(__file__))

class CommandLineInterfaceTests(unittest.TestCase):

    def test_CLI(self):
        # these are examples and will fail
        # TODO: update these to actually test CLI
        runner = CliRunner()
        result = runner.invoke(main, 
                               f'''--input-path {os.path.join(test_dir,'test_data','test_data.csv')}
                                --output-directory {os.path.join(test_dir,'testout')}
                                --num-runs 2
                                --max-topic 10
                                --pretrained False
                                --shiny-start False''')
        self.assertIsNone(result.exception)


if __name__ == "__main__":

    unittest.main(verbosity=2)

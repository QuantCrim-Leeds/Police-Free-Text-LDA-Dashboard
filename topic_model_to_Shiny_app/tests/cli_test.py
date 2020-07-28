import os
import unittest
from unittest.mock import patch
import pkg_resources
from click.testing import CliRunner
from topic2shiny import main

resource_package = 'topic_model_to_Shiny_app'

test_dir = os.path.dirname(os.path.abspath(__file__))

class CLI_test(unittest.TestCase):

    def test_CLI(self):
        # these are examples and will fail
        # TODO: update these to actually test CLI
        runner = CliRunner()
        result = runner.invoke(cli, ['--debug', 'sync'])
        assert result.exit_code == 0
        assert 'Debug mode is on' in result.output
        assert 'Syncing' in result.output



if __name__ == "__main__":

    unittest.main(verbosity=2)

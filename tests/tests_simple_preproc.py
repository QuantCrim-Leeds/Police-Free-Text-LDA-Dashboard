# TODO
# these tests are not robust and just test whether functions run with dummy data
# need to include assert statements to validate the output against expected values

import os
import unittest
from unittest.mock import patch
from topic_model_to_Shiny_app import text_preprocessing
import pandas as pd

test_dir = os.path.dirname(os.path.abspath(__file__))

class Test(unittest.TestCase):

    @patch('topic_model_to_Shiny_app.text_preprocessing.initial_data_import', return_value=os.path.abspath('./test_data/test_data.csv'))
    def test_initial_data_import(self, input):

        self.data = text_preprocessing.initial_data_import()

    def test_validate_input_data(self):

        self.data = text_preprocessing.validate_input_data(pd.read_csv(os.path.join(test_dir, 'test_data/test_data.csv'),
                                                                       encoding='latin'))

    def test_doc_to_words(self):

        self.assertEqual(list(text_preprocessing.doc_to_words(['the world goes round? and round.'])),
                         [['the','world','goes','round','and','round']])

    def test_lem_word(self):

        self.assertEqual(text_preprocessing.lem_word([['rocks','corpora','feet']]),[['rock','corpus','foot']])

    def test_remove_stopwords(self):

        self.assertEqual(text_preprocessing.remove_stopwords([['the','and','jackal']]), [['jackal']])

    @patch('topic_model_to_Shiny_app.text_preprocessing.preprocessing', return_value=os.path.abspath('./test_data/test_data.csv'))
    def test_full(self, input):

        self.data = text_preprocessing.preprocessing()

if __name__ == "__main__":
    unittest.main()

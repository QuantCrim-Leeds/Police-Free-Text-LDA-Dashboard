# TODO
# these tests are not robust and just test whether functions run with dummy data
# need to include assert statements to validate the output against expected values

import os
import unittest
import pandas as pd
from topic_model_to_Shiny_app import topic_number_selex
from gensim.test.utils import common_texts, common_dictionary, common_corpus

test_dir = os.path.dirname(os.path.abspath(__file__))

class Test(unittest.TestCase):

    def test_data_import(self):

        self.data = topic_number_selex.load_preprocessed()

    def test_processing(self):

        self.data = topic_number_selex.bag_of_word_processing(common_texts)

    def test_wide_coherence_search(self):

        self.data = topic_number_selex.calculate_scores(dictionary = common_dictionary,
                                                        corpus = common_corpus,
                                                        texts = common_texts,
                                                        limit = 5,
                                                        start = 2, step = 3)

    def test_narrow_coherence_search(self):

        self.data = topic_number_selex.calculate_scores_x3(dictionary = common_dictionary,
                                                           corpus = common_corpus,
                                                           texts = common_texts,
                                                           topic_n = range(5, 5 + 6),
                                                           narrow_iter=2)


    def test_build_model(self):

        self.data = topic_number_selex.build_optimum_model(repeated_test_frame = pd.DataFrame.from_dict({ 2 : [0.5],
                                                                                                         2 : [0.45],
                                                                                                         2 : [0.43],
                                                                                                         3 : [0.47],
                                                                                                         3 : [0.3],
                                                                                                         4 : [0.36],
                                                                                                         4 : [0.39],
                                                                                                         5 : [0.46],
                                                                                                         5 : [0.48]}),
                                                          corpus = common_corpus,
                                                          dictionary = common_dictionary,
                                                          texts = common_texts)


if __name__ == "__main__":
    unittest.main()

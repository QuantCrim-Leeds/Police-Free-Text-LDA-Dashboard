# TODO
# these tests are not robust and just test whether functions run with dummy data
# need to include assert statements to validate the output against expected values
# issues with relative paths

import os
import unittest
import numpy as np
import pandas as pd
from topic_model_to_Shiny_app import dominant_topic_processing
import gensim.models.ldamodel
from gensim.test.utils import common_texts
from gensim.corpora import Dictionary

test_dir = os.path.dirname(os.path.abspath(__file__))

dictionary = Dictionary(common_texts)
corpus = [dictionary.doc2bow(text) for text in common_texts]


class Test(unittest.TestCase):

    def setUp(self):

        self.class_ = gensim.models.ldamodel.LdaModel

        self.model = self.class_(corpus, id2word=dictionary, num_topics=3)

    def test_format_topics(self):

        model1 = self.class_(corpus, id2word=dictionary, num_topics=3)

        self.data = dominant_topic_processing.format_topics_sentences(model1, corpus, common_texts)

        self.assertEqual(type(self.data), type(pd.DataFrame()))

    def test_LSOA_matcherr(self):

        self.test_data = pd.read_csv('./tests/test_data/PC_to_match.csv', index_col=False)

        self.data = dominant_topic_processing.LSOA_to_PC_matcher(self.test_data)

        # use numpy function to test if arrays are the same
        np.testing.assert_array_equal(self.data[0], self.test_data.MSOA.str.split(',', expand=True).values[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)

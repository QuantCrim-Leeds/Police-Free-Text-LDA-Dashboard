# TODO
# these tests are not robust and just test whether functions run with dummy data
# need to include assert statements to validate the output against expected values

import os
import unittest
from unittest.mock import patch
import pandas as pd
from topic_model_to_Shiny_app import text_preprocessing, topic_number_selex, dominant_topic_processing
import gensim.models.ldamodel
from gensim.corpora import Dictionary
from gensim.test.utils import common_texts, common_dictionary, common_corpus
import pkg_resources

dictionary = Dictionary(common_texts)
corpus = [dictionary.doc2bow(text) for text in common_texts]

resource_package = 'topic_model_to_Shiny_app'

test_dir = os.path.dirname(os.path.abspath(__file__))

class Test(unittest.TestCase):

    def setUp(self):

        self.class_ = gensim.models.ldamodel.LdaModel

        self.model = self.class_(corpus, id2word=dictionary, num_topics=3)

    @patch('builtins.input',return_value=pkg_resources.resource_filename(resource_package, 'tests/test_data/test_data.csv'))
    def test_initial_data_import(self, input):

        self.data = text_preprocessing.initial_data_import()

        print(self.data)

        self.assertTrue(isinstance(self.data, pd.DataFrame))

    def test_validate_input_data(self):

        self.data = text_preprocessing.validate_input_data(
                    pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/test_data/test_data.csv'),
                                                                       encoding='latin'))

        self.assertEqual(self.data.CrimeNotes.isna().sum(), 0)

    def test_doc_to_words(self):

        self.assertEqual(list(text_preprocessing.doc_to_words(['the world goes round? and round.'])),
                         [['the','world','goes','round','and','round']])

    def test_lem_word(self):

        self.assertEqual(text_preprocessing.lem_word([['rocks','corpora','feet']]),[['rock','corpus','foot']])

    def test_remove_stopwords(self):

        self.assertEqual(text_preprocessing.remove_stopwords([['the','and','jackal']]), [['jackal']])

    @patch('builtins.input',return_value=pkg_resources.resource_filename(resource_package,' tests/test_data/test_data.csv'))
    def test_full_preprocessing(self, input):

        self.data = text_preprocessing.preprocessing()

        self.assertTrue(isinstance(self.data, pd.DataFrame))

        self.assertEqual(self.data.CrimeNotes.isna().sum(), 0)

    def test_processed_data_import(self):

        self.frame = pd.read_csv(pkg_resources.resource_filename(resource_package, 'tests/test_data/test_processed_data.csv'), encoding='latin')

        self.data = topic_number_selex.load_preprocessed(self.frame)

        self.assertTrue(isinstance(self.data, list))

    def test_processing(self):

        self.data = topic_number_selex.bag_of_word_processing(common_texts)

    def test_wide_coherence_search(self):

        self.data = topic_number_selex.calculate_scores(dictionary = common_dictionary,
                                                        corpus = common_corpus,
                                                        texts = common_texts,
                                                        limit = 5,
                                                        start = 2, step = 3)

        self.assertTrue(isinstance(self.data, pd.DataFrame))

        self.assertEqual(self.data.columns.tolist(), ['Num_topics','Coherence_score'])

    def test_narrow_coherence_search(self):

        self.data = topic_number_selex.calculate_scores_x3(dictionary = common_dictionary,
                                                           corpus = common_corpus,
                                                           texts = common_texts,
                                                           topic_n = range(5, 5 + 6),
                                                           narrow_iter=2)

        self.assertTrue(isinstance(self.data, pd.DataFrame))


    def test_build_model(self):

        self.input_dict = (pd.DataFrame.from_dict({ 2 : [0.5],
                                                 2 : [0.45],
                                                 2 : [0.43],
                                                 3 : [0.47],
                                                 3 : [0.3],
                                                 4 : [0.36],
                                                 4 : [0.39],
                                                 5 : [0.46],
                                                 5 : [0.48]}))

        self.data = topic_number_selex.build_optimum_model(repeated_test_frame = self.input_dict,
                                                          corpus = common_corpus,
                                                          dictionary = common_dictionary,
                                                          texts = common_texts)


    def test_format_topics(self):

        model1 = self.class_(corpus, id2word=dictionary, num_topics=3)

        self.data = dominant_topic_processing.format_topics_sentences(model1, corpus, common_texts)

        self.assertTrue(isinstance(self.data, pd.DataFrame))

    def test_LSOA_matcherr(self):

        self.test_data = pd.read_csv(pkg_resources.resource_filename(resource_package,'tests/test_data/PC_to_match.csv'),
                                     index_col=False)

        self.data = dominant_topic_processing.OA_to_PC_matcher(self.test_data)[0].split(',')

        self.data_match = self.test_data.MSOA.str.split(',', expand=True).values.tolist()[0]

        # function returns list, so assert list items are equal
        self.assertCountEqual(self.data, self.data_match)

    def test_get_top3(self):
        """
        this is a integration style test taking output of format_topics_sentences
        TODO: Make this a proper unit test
        """

        model1 = self.class_(corpus, id2word=dictionary, num_topics=3)

        self.data = dominant_topic_processing.format_topics_sentences(model1, corpus, common_texts)

        self.top3 = dominant_topic_processing.get_top3_docs(self.data)

        self.assertTrue(isinstance(self.top3, pd.DataFrame))


    # integration test
    @patch('builtins.input',return_value=pkg_resources.resource_filename(resource_package, 'tests/test_data/test_data.csv'))
    def int_test(self, input):

        # run preprocessing function
        # should save data into right places for next function

        self.data = text_preprocessing.preprocessing()

        # run topic selector function using output from above preprocessing
        self.data = topic_number_selex.topic_number_selector(self.data, narrow_iter=2)

        # run dominant topic processing
        self.data = dominant_topic_processing.topic_processing()

        # check output file exists by loading as pandas and comparing
        assertEqual(isinstance(pd.read_csv(pkg_resources.resource_filename(resource_package,'data/transformed_data_source.csv'),
                               pd.DataFrame)))

if __name__ == "__main__":

    unittest.main(verbosity=2)

# script for determining optimal topic number
# import libraries

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import gensim
from gensim.corpora import Dictionary
from gensim.models import CoherenceModel
from sklearn.externals import joblib
import nltk


# specify path to mallet
mallet_path = './mallet-2.0.8/bin/mallet' # update this path

def topic_number_selector(narrow_iter=2):
    """
    A function for determining the optimal topic number based on coherence score.
    narrow_iter = number of LDA model repeats

    Inputs:
    mallet_path = the path to mallet binaries
    the data_processed.pkl file from text_preprocessing.py, contains preprocessed text

    Outputs:
    broad_topic_k_search graph file to Files dir
    multiple_run_ktopics graph file to Files dir
    working_ldamallet_model.gensim to model dir
    saves BoW corpus data dir
    """

    print('Beginning topic number optimisation.')

    # load data with tokens
    crimenotes_corpus = load_preprocessed()

    # create a dictionary and a corpus in BoW format
    dictionary, corpus = bag_of_word_processing(crimenotes_corpus)

    # run broad coherence scan
    model_list, coherence_df  = calculate_scores(dictionary=dictionary,
                                                 corpus=corpus,
                                                 texts=crimenotes_corpus,
                                                 start=2, limit=100, step=5)

    # identify the topic number with the highest coherence score
    wide_coh_score = coherence_df['Num_topics'].max()

    # use the best topic number to run repeat LDA runs to confirm it scores best
    df_x3 = calculate_scores_x3(dictionary=dictionary,
                                corpus=corpus,
                                texts=crimenotes_corpus,
                                topic_n=range(wide_coh_score, wide_coh_score + 6),
                                narrow_iter=narrow_iter)

    build_optimum_model(df_x3, corpus, dictionary, crimenotes_corpus)

def load_preprocessed():
    """Load preprocessed data.

    Check tokens are included.
    Prepare tokens into a list for dictionary preparation
    Output analysis of word frequency across entire corpus

    """
    # import data
    combined_df = pd.read_csv("./data/data_processed.csv", index_col=0)

    # test to ensure tokens are included, will crash if not present
    combined_df['Tokens'] == True

    # convert tokens column to list for dictionary and corpus BoW generation
    token_corpus = combined_df['Tokens_str'].str.split(',').tolist()

    # lets do quick analysis without ngrams

    # visualise word frequency
    # flatten list of lists into 1D list
    flat_list = [item for sublist in token_corpus for item in sublist]

    print(len(flat_list))
    # convert text to nltk text object
    text = nltk.Text(flat_list)

    # frequency of words
    fdist = nltk.FreqDist(text)
    print(fdist.most_common(50))

    return token_corpus


def bag_of_word_processing(corpus_of_tokens):
    """
    Take the list of tokens and convert them into a bag-of-words (BoW) format.

    A dictionary of word-unique number pairs is created
    Along with converting the corpus into numbers corresponding to the word in the Dictionary

    Outputs:
    BoW corpus
    BoW dictionary
    Shows average number of words per document
    """

    # Create a dictionary representation of the documents.
    # gensim Dictionary function creates tokens -> tokenID dict
    dictionary = Dictionary(corpus_of_tokens)
    print('Number of unique words in initital documents:', len(dictionary))

    org_dict = len(dictionary)

    # determine lower limit of extreme filter for Dictionary
    min_limit = int(len(corpus_of_tokens) / 1000)

    print('Minimum limit for extremes filter is: ',str(min_limit))

    # Filter out words that occur less than 10 documents, or more than 70% of the documents.
    dictionary.filter_extremes(no_below=min_limit, no_above=0.7)
    print('Number of unique words after removing rare and common words:', len(dictionary))

    filt_dict = len(dictionary)

    print('Token reduction of: ' + str((1-filt_dict/org_dict)*100)+'%')

    # transform to bag of words
    corpus = [dictionary.doc2bow(doc) for doc in corpus_of_tokens]
    print('Number of unique tokens: %d' % len(dictionary))
    print('Number of documents: %d' % len(corpus))

    # output on document length
    print('Average number of words per document: ',np.mean([len(corpus[i]) for i in range(len(corpus))]))

    return dictionary, corpus
    # topic number determination

def calculate_scores(dictionary, corpus,  texts, limit, start=2, step=3):
    """
    Compute c_v coherence for a wide range of topic numbers.
    Adapted from https://www.machinelearningplus.com/nlp/topic-modeling-gensim-python/

    Parameters:
    ----------
    dictionary : Gensim dictionary
    corpus : Gensim corpus
    method = c_v or u_mass
    texts : List of input texts (doc_clean)
    limit : Max num of topics

    Returns:
    -------
    model_list : List of LDA topic models
    coherence_values : Coherence values corresponding to the LDA model with respective number of topics
    graphical outputs
    """
    coherence_dict = dict()
    model_list = []

    for num_topics in range(start, limit, step):
        model = gensim.models.wrappers.LdaMallet(mallet_path, corpus=corpus, num_topics=num_topics, id2word=dictionary)
        model_list.append(model)
        coherencemodel1 = CoherenceModel(model=model, texts=texts, dictionary=dictionary, coherence='c_v')
        coherence_dict[num_topics] = coherencemodel1.get_coherence()

    coherence_df = pd.DataFrame(pd.Series(coherence_dict)).reset_index()

    coherence_df.columns = ['Num_topics','Coherence_score']

    # Show graph
    x = range(start, limit, step)
    fig, ax = plt.subplots(figsize=(12,10))
    ax.plot(coherence_df['Num_topics'], coherence_df['Coherence_score'])
    ax.set_xlabel("No. of topics", fontweight='bold')
    ax.set_ylabel("Cv Coherence score", fontweight='bold')
    ax.axvline(coherence_df[coherence_df['Coherence_score'] == coherence_df['Coherence_score'].max()]['Num_topics'].tolist(), color='red')
    fig.savefig('./Files/broad_topic_k_search.png', format='png',dpi=300)

    return model_list, coherence_df


def calculate_scores_x3(dictionary, corpus,  texts, topic_n, narrow_iter=2):
    """
    Compute c_v coherence for for a narrow range of topics in replicate.

    Adapted from https://www.machinelearningplus.com/nlp/topic-modeling-gensim-python/

    Parameters:
    ----------
    dictionary : Gensim dictionary
    corpus : Gensim corpus
    method = c_v or u_mass
    texts : List of input texts (doc_clean)
    limit : Max num of topics

    Returns:
    -------
    final_df : dataframe of coherence scores
    """

    final_coh_list = []

    for i in topic_n:

        coherence_values1 = []

        for x in range(narrow_iter):
            model = gensim.models.wrappers.LdaMallet(mallet_path, corpus=corpus, num_topics=i, id2word=dictionary)
            coherencemodel1 = CoherenceModel(model=model, texts=texts, dictionary=dictionary, coherence='c_v')
            coherence_values1.append(coherencemodel1.get_coherence())

        final_coh_list.append(coherence_values1)

    plt.boxplot(final_coh_list, positions=topic_n)

    # transpose dataframe into one row of coherence scores
    final_df = pd.DataFrame(final_coh_list).T

    # name each column the topic number used
    final_df.columns = topic_n

    # produce and save a graphical output of the coherence scores
    plt.rcParams.update({'font.size': 16})
    fig, ax = plt.subplots(figsize=(12,10))
    ax.boxplot(final_df.values, positions=final_df.columns.tolist())
    ax.set_xlabel('No. of topics', fontweight='bold')
    ax.set_ylabel('Cv Coherence Score', fontweight='bold')
    fig.savefig('./Files/multiple_run_ktopics.png',format='png', dpi=300)

    return final_df


def build_optimum_model(repeated_test_frame, corpus, dictionary, texts):

    """
    Build and save a topic model based on topic number determined by coherence score searches.

    Save gensim model and BoW corpus

    """

    repeated_test_frameT = repeated_test_frame.describe().T

    # find the highest mean with the narrowest interquartile range (most consistent)
    optimum_topic_k = (pd.Series(repeated_test_frameT['mean']) - pd.Series(repeated_test_frameT['75%'] - repeated_test_frameT['25%'])).sort_values(ascending=False).index.tolist()[0]

    print('The optimum topic number is: ', optimum_topic_k)
    print('The coherence score for this number is: ', (pd.Series(repeated_test_frameT['mean']) - pd.Series(repeated_test_frameT['75%'] - repeated_test_frameT['25%'])))

    # now create a working model using this data

    working_ldamallet = gensim.models.wrappers.LdaMallet(mallet_path,
                                                corpus = corpus,
                                                num_topics = int(optimum_topic_k),
                                                id2word = dictionary,
                                                prefix = './model/')
    print('Model trained.')
    coherencemodel1 = CoherenceModel(model = working_ldamallet,
                                     texts = texts,
                                     dictionary = dictionary,
                                     coherence = 'c_v')

    print('Working model coherence score: ', coherencemodel1.get_coherence())

    # save new working model
    working_ldamallet.save('./model/working_ldamallet_model.gensim')

    gensim.corpora.MmCorpus.serialize("./data/BoW_corpus.mm", corpus)
    print('Model saved.')

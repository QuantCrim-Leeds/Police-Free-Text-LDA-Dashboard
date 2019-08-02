# script for preprocessing text data for LDA
# import libraries
import sys
import numpy as np
import pandas as pd
import gensim
import nltk
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer

nltk.download('stopwords')
nltk.download('wordnet')

# main function that performs preprocessing
def preprocessing():
    """Complete preprocessing script that outputs dataframe with new tokens column."""

    working_dataframe = initial_data_import()

    validated_dataframe = validate_input_data(working_dataframe)

    crime_notes = validated_dataframe['CrimeNotes'].tolist()

    words = list(doc_to_words(crime_notes))
    print('Data tokenised.')

    words = lem_word(words)
    print('Tokens lemmatised.')

    words = remove_stopwords(words)

    print('Stopwords removed.')

    validated_dataframe.loc[:,'Tokens'] = words

    #create string joined by , if tokens present else add NaN
    validated_dataframe.loc[:,'Tokens_str'] = validated_dataframe['Tokens'].apply(lambda x: ','.join(map(str, x)) if len(x) != 0 else np.NaN)

    # the above function renders empty lists as NaN
    # must be removed here and not later
    # TODO this could be included elsewhere
    validated_dataframe = validated_dataframe.dropna(axis=0, subset=['Tokens_str'])

    output_processed_data(validated_dataframe)

    return validated_dataframe


def initial_data_import():
    """Imports initial .csv dataframe converts into pandas object."""

    print('Beginning text preprocessing.')
    # specifying data directory

    data_path = str(input('Specify the full path to the input :'))

    # validate that the file format is .csv

    if str(data_path[-4:]) != '.csv':
        print('Please confirm you are passing a .csv file type.')

    # reading data
    original_frame = pd.read_csv(data_path.strip(), encoding='latin1')

    return original_frame


def validate_input_data(data):
    """Performs some data validation: checking required columns and removing duplicate text documents."""

    desired_cols = ["URN",
                    "CrimeType",
                    "OccType",
                    "Day",
                    "Month",
                    "PartialPostCode",
                    "MODescription",
                    "CrimeNotes",
                    "HOClass",
                    "OffenceRec",
                    "DomViol"]

    # validate columns passed are the columns expected
    col_check = pd.Series(desired_cols).isin(data.columns)

    if min(col_check) != 1:

        missing_cols = pd.Series(desired_cols)[col_check]

        print('Could not find the following expected columns %s' % str(missing_cols))

        sys.exit()
    else:
        print('Expected columns found.')
        print('Moving onto NA and duplicate validation.')

    # print out reports on number of NAs and number of duplicate entries
    print('The number of NA fields in this data:')
    print(data.isna().sum())

    print('Count of duplicates in URN, CrimeNotes fields:')
    for x in ['URN', 'CrimeNotes']:
        print(x,'-', data[x].duplicated().sum())

    print('Removing duplicated or NA text documents.')
    # drop any duplicated reports
    no_dup_data = data.drop_duplicates(subset='CrimeNotes', keep='first')

    no_dup_data.dropna(axis=0, subset=['CrimeNotes'], inplace=True)

    no_dup_data.reset_index(drop=True, inplace=True)

    print('Number of duplicated documents check(should be zero):', str(no_dup_data['CrimeNotes'].duplicated().sum()))

    return no_dup_data


# need to tokenise words within corpus for passing to LDA algorithmn
def doc_to_words(sentences):
    """Simple tokeniser from gensim removes punctuations and converts everything to lowercase."""
    for sentence in sentences:
        # use gensim tokenisation system, doc must be string, deaccent function given as true
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))


# lemmatisation of tokens
def lem_word(words):
    """Wordnet lemmatization: converting words to their root or lemma (alternative method to stemming)."""
    lemma = WordNetLemmatizer()
    # this function takes a list of lists of tokens
    return [[lemma.lemmatize(token) for token in tokens] for tokens in words]


def remove_stopwords(text):
    """Removes stopwords using WordNet english list and and additionals passed to stopword.txt file."""
    # removing stop words from the data
    stop_words = stopwords.words('english')
    stop_words.extend([line.strip() for line in open('./data/stopwords.txt')])

    return [[word for word in gensim.utils.simple_preprocess(str(doc)) if word not in stop_words] for doc in text]


def n_gram(tokens):
    """Identifies common two/three word phrases using gensim module."""
    # Add bigrams and trigrams to docs (only ones that appear 10 times or more).
    # includes threshold kwarg (threshold score required by bigram)
    bigram = gensim.models.phrases.Phrases(tokens, min_count=10, threshold=100)
    trigram = gensim.models.phrases.Phrases(bigram[tokens], threshold = 100)

    for idx, val in enumerate(tokens):
        for token in bigram[tokens[idx]]:
            if '_' in token:
                if token not in tokens[idx]:
                    # Token is a bigram, add to document.bigram
                    tokens[idx].append(token)
        for token in trigram[tokens[idx]]:
            if '_' in token:
                if token not in tokens[idx]:
                    # Token is a trigram, add to document.
                    tokens[idx].append(token)

    print('Bigrams and trigrams created.')


def output_processed_data(dataframe):
    """ Outputs dataframe with tokenised data in a new column as a .csv"""
    # saves dataframe and processed corpus of tokens
    dataframe.to_csv('./data/data_processed.csv')

    print('Data saved in data folder. Preprocessing complete.')

    return

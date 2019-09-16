# script for performing dominant topic clustering using trained LDA model
# entire thing is a TODO
# TODO DOCSTRINGS!
# TODO ordering of dominant_topic_processing function needs function calls adding
# develop some unit tests
# import libraries
import pandas as pd
import matplotlib.pyplot as plt
import gensim
from gensim.corpora.mmcorpus import MmCorpus
import pkg_resources

# specify top level package folder
resource_package = 'topic_model_to_Shiny_app'


def topic_processing():
    """
    Applying dominant topic labelling to processed corpus.
    -------
    Inputs:
    combined_df = main dataframe includes tokens
    ldamallet = working mallet model determined in topic_number_selex.py
    lsoaPC_df = PC_to_LSOA_dec2011.csv dataframe for postcode to MSOA matching

    Outputs:
    LDA_topics.txt file = raw topic word-probability outputs
    Example_MOs_per_topic.csv file = snapshot of docs in each topic for inspection
    transformed_data_source.csv = modified original dataframe for app
    --------
    """

    print('Starting dominant topic processing.')

    (corpus, ldamallet, combined_df) = load_model()

    top20_df = format_topics_sentences(ldamodel=ldamallet, corpus=corpus, texts=combined_df['CrimeNotes'])

    print('Dominant topic segmentation complete.')

    # commenting out for testing
    representative_docs = get_top3_docs(top20_df)

    representative_docs.to_csv(pkg_resources.resource_filename(resource_package, 'Files/Example_MOs_per_topic.csv'))

    print('Example MOs written to Files folder.')

    data_for_app = data_preparations(combined_df, top20_df)

    data_for_app.to_csv(pkg_resources.resource_filename(resource_package, 'data/transformed_data_source.csv'))

    print('Transformed data saved in data folder.')

    print('Dominant topic processing complete.')

    return


# is this necessary if we don't have a model?
def load_model():
    """
    Load working model

    Loads working model, BoW corpus and initial dataframe with tokens

    Outputs:
    Writes a .txt file of top 7 words per topic for subsequent inspection.
    """

    # load data
    combined_df = pd.read_csv(pkg_resources.resource_filename(resource_package, "data/data_processed.csv"), index_col=0)

    corpus = MmCorpus(pkg_resources.resource_filename(resource_package, "data/BoW_corpus.mm"))
    print('Data loaded.')
    # load the mallet model
    ldamallet = gensim.models.wrappers.LdaMallet.load(pkg_resources.resource_filename(resource_package, 'model/working_ldamallet_model.gensim'))
    print('Model loaded.')
    # write out topics to a text file
    topics = ldamallet.print_topics(num_topics=-1, num_words=7)

    with open(pkg_resources.resource_filename(resource_package, 'Files/LDA_topics.txt'), 'w') as topic_file:
        for topic in topics:
            topic_file.write(str(topic) + '\n')
    print('Topics written to data folder.')

    return (corpus, ldamallet, combined_df)

# inputs are model, corpus and original texts
def format_topics_sentences(ldamodel, corpus, texts):
    # Init output
    sent_topics_df = pd.DataFrame()

    # Get main topic in each document
    # enumerate each topic and return number of topic, row of topic numbers and probabilities
    for row in ldamodel[corpus]:
        # sort row data into descending order
        row = sorted(row, key=lambda x: (x[1]), reverse=True)
        # Get the Dominant topic, Perc Contribution and Keywords for each document
        # split row value into j (numerated), topic number, topic probability
        # select top numerated (top ranked topic), retrieve topic text and join it altogether
        # combine into pandas dataframe with topic text and probability of topic
        for j, (topic_num, prop_topic) in enumerate(row):
            if j == 0:  # => dominant topic
                wordprob = ldamodel.show_topic(topic_num)
                topic_keywords = ", ".join([word for word, prop in wordprob])
                sent_topics_df = sent_topics_df.append(pd.Series([int(topic_num) + 1,
                                                                  round(prop_topic, 4),
                                                                  topic_keywords]), ignore_index=True)
            else:
                break

    # Add original text to the end of the output
    contents = pd.Series(texts)
    sent_topics_df = pd.concat([sent_topics_df, contents], axis=1)
    # add column names
    sent_topics_df.columns = ['Dominant_Topic', 'Perc_Contribution', 'Topic_Keywords', 'Original text']

    # get a graphic of number of docs per topic
    sent_topics_df['Dominant_Topic'].value_counts().sort_index().plot(kind='bar', figsize=(12, 10))
    plt.xlabel('Topic number', fontweight='bold')
    plt.ylabel('Number of docs', fontweight='bold')
    plt.savefig(pkg_resources.resource_filename(resource_package, 'Files/Docs_per_Topic.png'), format='png', dpi=300)

    return sent_topics_df


def get_top3_docs(dominant_topic_frame):

    table_lst = []

    # create dataframe of top 3 most representative docs for each topic
    for i in range(1, int(dominant_topic_frame['Dominant_Topic'].max())):
        # get indexes
        indy = dominant_topic_frame[dominant_topic_frame['Dominant_Topic'] == i].sort_values(by='Perc_Contribution', ascending=False).index.tolist()
        # test how many documents passed
        if len(indy) <= 3:
            for idx in indy:
                table_lst.append(dominant_topic_frame.iloc[idx, :])
        else:
            table_lst.append(dominant_topic_frame.iloc[indy[0], :])
            table_lst.append(dominant_topic_frame.iloc[indy[1], :])
            table_lst.append(dominant_topic_frame.iloc[indy[2], :])

    new_eg_df = pd.DataFrame(table_lst)

    return new_eg_df



# create labelled original dataframe for output as source to R shiny app
def data_preparations(data_source, dominant_topic_frame):

    print('Commencing data preparation for app.')

    app_data_source = data_source.copy()

    app_data_source['LDA_Topic'] = dominant_topic_frame['Dominant_Topic']

    app_data_source['Topic_keywords'] = dominant_topic_frame['Topic_Keywords']

    # select required columns for application
    app_data_source = app_data_source.loc[:, ['Month',
                                              'PartialPostCode',
                                              'Year',
                                              'CrimeNotes',
                                              'LDA_Topic',
                                              'Topic_keywords',
                                              'Tokens']]

    # for now we'll run this app for data for one year only
    #app_data_source['Month_Year'] = app_data_source['Month'].map(str) + app_data_source['Year'].astype(str)

    app_data_source.loc[:, 'MSOA'] = OA_to_PC_matcher(app_data_source)

    # TODO unclear this is necessary
    # section string reformatting for choropleth mapping
    #app_data_source.loc[:, 'MSOA'] = app_data_source['MSOA'].str.strip("[]")

    #app_data_source.loc[:, 'MSOA'] = app_data_source['MSOA'].str.replace("'", "")

    #app_data_source.loc[:, 'MSOA'] = app_data_source['MSOA'].str.replace(" ", "")

    # configure dates into unique integers
    mon_y1_dict = {'Jan' :1,
                   'Feb' : 2,
                   'Mar' : 3,
                   'Apr' : 4,
                   'May' : 5,
                   'Jun' : 6,
                   'Jul' : 7,
                   'Aug' : 8,
                   'Sep' : 9,
                   'Oct' : 10,
                   'Nov' : 11,
                   'Dec' : 12}

    # convert month year dates to integers
    app_data_source['Month2'] = app_data_source['Month'].map(mon_y1_dict)

    return app_data_source


def OA_to_PC_matcher(app_data):
    """
    Matches partial postcodes to MSOA codes

    Loads census provided postcode,LSOA,MSOA codes for matching

    Requires the column PartialPostCode in dataframe to be passed.

    Outputs pd.Series of unique MSOA codes matched for each PartialPostCode

    """
    # open dataframe for postcode matching to MSOA
    lsoaPC_df = pd.read_csv(pkg_resources.resource_filename(resource_package, 'data/PC_to_LSOA_dec2011.csv'))

    # resolve postcode spacing
    lsoaPC_df['PCD7'] = lsoaPC_df['PCD7'].str.replace(' ', '')

    # reset index
    lsoaPC_df = lsoaPC_df.reset_index()

    MSOA_in_PC = []

    # section matching postcode to MSOA codes
    print('Matching postcodes to MSOA. This may take sometime.')

    for x in app_data['PartialPostCode']:

        matched_MSOA = lsoaPC_df[lsoaPC_df['PCD7'].str.contains(x)].loc[:, 'MSOA11CD'].unique()

        MSOA_in_PC.append(','.join(matched_MSOA))

    # return pandas series of MSOAs in order of passed frame
    return MSOA_in_PC

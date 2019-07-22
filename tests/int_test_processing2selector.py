# building this script as a integration test
# i'm not testing the full output against anything other than visual expectations
# i know this isn't ideal so TODO improvements
# general structure here is that of final master_run script
from topic_model_to_Shiny_app import text_preprocessing, topic_number_selex, dominant_topic_processing


def int_test():

    # run preproccesing function
    # should save data into right places for next function
    text_preprocessing.preproccesing()

    # run topic selector function using output from above preprocessing
    topic_number_selex.topic_number_selector(narrow_iter=2)

    # run dominant topic processing
    dominant_topic_processing.topic_processing()


if __name__ == "__main__":
    int_test()

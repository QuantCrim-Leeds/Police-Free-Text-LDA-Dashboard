# TODO: complete this script

import time
import os
import subprocess
from topic_model_to_Shiny_app.text_preprocessing import preprocessing
from topic_model_to_Shiny_app.topic_number_selex import topic_number_selector
from topic_model_to_Shiny_app.dominant_topic_processing import topic_processing

# for complete script timing
def main():
    start = time.time()

    print('Initialising please specify the following parameters.')

    LDA_repeats = int(input("""Please specify the number of LDA repeats for topic number selection\n(n.b The more repeats the longer the runtime): """))

    existing_model = input('Have you pretrained a working model? (Yes, No) ')

    print(existing_model)
    # check if you need a new model
    if existing_model.lower() == 'no':

        preprocessing()

        topic_number_selector(narrow_iter=LDA_repeats)

    else:
        pass

    topic_processing()

    end = time.time()

    print('Time elapsed: ',end-start)

    print('Initialising Shiny dashboard.')

    shiny_dir = os.path.abspath("Shiny/combined.R")

    # process to call shiny app
    # TODO: this partial path call is a security issue
    subprocess.call([shiny_dir])

if __name__ == '__main__':

    main()

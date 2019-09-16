# TODO: complete this script

import time
import os
# consider security imp of subprocess
import subprocess
from topic_model_to_Shiny_app.text_preprocessing import preprocessing
from topic_model_to_Shiny_app.topic_number_selex import topic_number_selector
from topic_model_to_Shiny_app.dominant_topic_processing import topic_processing
import pkg_resources

# specify top level package folder
resource_package = 'topic_model_to_Shiny_app'

# for complete script timing
def main():
    start = time.time()

    print('Initialising please specify the following parameters.')

    LDA_repeats = int(input("""Please specify the number of LDA repeats for topic number selection\n(n.b The more repeats the longer the runtime): """))

    output_path = str(input('Specify a path for output files: '))

    pathlib.Path(output_path).mkdir(parents=False, exist_ok=True)

    existing_model = input('Have you pretrained a working model? (Yes, No) ')

    print(existing_model)
    # check if you need a new model
    if existing_model.lower() == 'no':

        transformed_data = preprocessing()

        topic_number_selector(processed_data = transformed_data, output_path=output_path,
                              narrow_iter = LDA_repeats, wide_iter = 100)

    else:
        pass

    topic_processing(output_path=output_path)

    end = time.time()

    print('Time elapsed: ',end-start)

    print('Initialising Shiny dashboard.')

    shiny_dir = pkg_resources.resource_filename(resource_package, "Shiny/combined.R")

    # process to call shiny app
    # TODO: this partial path call is a security issue
    subprocess.call([shiny_dir])

if __name__ == '__main__':

    main()

import time
# consider security imp of subprocess
import subprocess
import click
from topic_model_to_Shiny_app.text_preprocessing import preprocessing
from topic_model_to_Shiny_app.topic_number_selex import topic_number_selector
from topic_model_to_Shiny_app.dominant_topic_processing import topic_processing
import pkg_resources
import pathlib

# specify top level package folder
resource_package = 'topic_model_to_Shiny_app'

@click.command()
@click.option('-i', '--input-path', prompt='Specify input data path', type=str,
              help='The absolute path to the input data file.')
@click.option('-o', '--output-directory', prompt='Specify directory for outputs', type=str,
              help='The absolute path to an directory for outputs, will create a new directory if required.')
@click.option('-n', '--num-runs', prompt='Please specify the number of LDA repeats for topic number selection', type=int,
              help='The number of LDA repeat runs desired to establish working topic number.')
@click.option('-m', '--max-topic', prompt='Please specify the upper bound of topic numbers to search for an optimal topic number', type=int,
              help='A maximum number of topics to fit models too when looking for an optimal topic number.', default=100)
@click.option('-p', '--pretrained', default=False, type=bool,
              help='A boolean to check if user wishes to use a pretrained model.')
@click.option('-m', '--pretrained-model', type=str,
              help='The absolute path to the pretrained model file.')
@click.option('-s', '--shiny-start', default=True, type=bool,
              help='A boolean to confirm if user wishes Shiny app instance to start.')
              
def main(input_path : str, 
         output_directory : str,
         num_runs : int, 
         max_topic : int,
         pretrained : bool, 
         pretrained_model : str,
         shiny_start : bool):
    """
    The main function handling CLI

    \b
    :param input_path: this is a first param 
    :param output_directory: this is a second param 
    :param n_runs: an integer of the number of repeat runs of LDA to perform
    :param pretrained: a boolean of whether user wants to use a pretrained model
    :param pretrained_model: a string of the path to the pretrained model
    :param shiny_start: a boolean of whether to start shiny app at the end of processing
    :returns: None (loads shiny app)
    """
    # take the output directory and create it if it doesn't exist
    pathlib.Path(output_directory).mkdir(parents=True, exist_ok=True)

    # check if you need a new model
    if not pretrained:

        transformed_data = preprocessing(input_path)

        topic_number_selector(processed_data = transformed_data, output_path=output_directory,
                              narrow_iter = num_runs, wide_iter = max_topic)

    else:
        # TODO: write in how to load a pretrained model
        pass

    topic_processing(output_path=output_directory)

    if shiny_start:

        print('Initialising Shiny dashboard.')

        shiny_dir = pkg_resources.resource_filename(resource_package, "Shiny/combined.R")

        # process to call shiny app
        subprocess.call([shiny_dir])

if __name__ == '__main__':

    main()

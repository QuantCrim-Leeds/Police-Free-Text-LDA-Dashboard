# lets test invoking Shiny application for final bit of application

import os
import subprocess

def invoke_Shiny():

    shiny_dir = os.path.abspath("Shiny/combined.R")
    # process to call shiny app
    # TODO: this partial path call is a security issue
    subprocess.call([shiny_dir])


if __name__ == '__main__':
    invoke_Shiny()

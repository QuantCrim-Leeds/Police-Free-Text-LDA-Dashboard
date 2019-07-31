# lets test invoking Shiny application for final bit of application

import os
import subprocess

def invoke_Shiny():
    # process to call shiny app
    subprocess.call(["./Shiny/combined.R"])


if __name__ == '__main__':
    invoke_Shiny()

# lets test invoking Shiny application for final bit of application

import os
import subprocess
import webbrowser

def invoke_Shiny():
    # process to call shiny app
    subprocess.call(["/usr/bin/Rscript --vanilla",os.path.join(os.getcwd(),"Shiny/combined.R")])

    #webbrowser.open()


if __name__ == '__main__':
    invoke_Shiny()

import time
import subprocess
import os
from topic_model_to_Shiny_app.text_preprocessing import text_preprocessing_start
from topic_model_to_Shiny_app.topic_number_selex import topic_number_selector
from topic_model_to_Shiny_app.LDA_dominant_topic_processing import dominant_topic_processing

# for complete script timing

start = time.time()

print('Initialising please specify the following parameters.')

LDA_repeats = int(input("""Please specify the number of LDA repeats for topic number selection\n(n.b The more repeats the longer the runtime): """))

existing_model = input('Have you pretrained a working model? (Yes, No) ')

print(existing_model)
# check if you need a new model
if existing_model.lower() == 'no':

    text_preprocessing_start()

    topic_number_selector(narrow_iter=LDA_repeats)

else:
    pass

dominant_topic_processing()

end = time.time()

print('Time elapsed: ',end-start)

# process to call shiny app
subprocess.call(["/usr/bin/Rscript","--vanilla",os.path.join(os.getcwd(),"Shiny/combined.R")])

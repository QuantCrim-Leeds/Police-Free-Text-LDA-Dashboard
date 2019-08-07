[![Build Status](https://travis-ci.com/Sparrow0hawk/topic_model_to_Shiny.svg?token=WAzszY1JKmTcLxy5prby&branch=master)](https://travis-ci.com/Sparrow0hawk/topic_model_to_Shiny)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/9bc12c76cc934008b3e081149de02b78)](https://www.codacy.com?utm_source=github.com&utm_medium=referral&utm_content=Sparrow0hawk/topic_model_to_Shiny&utm_campaign=Badge_Coverage)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/9bc12c76cc934008b3e081149de02b78)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Sparrow0hawk/topic_model_to_Shiny&amp;utm_campaign=Badge_Grade)

# Topic Model to Shiny App

This is an application of topic modelling (that determines topic number) using topic coherence rendering topic data into a Shiny App. This package utilises the Gensim natural language processing library (specificly its wrapper for the Mallet java topic modelling library)

## Included modules

text_preprocessing - text preprocessing script
topic_number_selex - topic number selection script (adjustable parameter controls the number of LDA repeats performed)
LDA_dominant_topic_processing - Dominant topic labelling

## Data format

Data format expected for this is:

| Identifier | CrimeType       | OccType         | Day               | Mon                 | PartialPostCode    | MODescription   | CrimeNotes  | HOClass     | OffenceRec      | DomViol |
| ---------- | --------------- | --------------- | ----------------- | ------------------- | ------------------ | --------------  | ----------- | ----------- | --------------- | ------- |
| int        | string category | string category | 3-letter day code | 3-letter month code | 4-5 level postcode | string keywords | string text | string code | string category | Y/N     |

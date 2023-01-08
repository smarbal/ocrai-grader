# OCRai
Automatic grader web application using AI OCR buit with Flask, Tailwind CSS + Flowbite and PaddleOCR.

## Installation 

Run
`docker-compose -up --build` in the root directory.  
The web page will be available at http://localhost:3000/.

## Features
- Users can upload files from storage or directly take a picture with their device.
- Images can be previewed and cropped before analysis.
- PDF files can be uploaded but can't be previewed or cropped. 
- History of processed files is available. 
- Results for any processed are viewable. 
- PNG or JSON exports are available. The JSON will contain arrays with the coordinates of text zones and their transcription; image will directly show the zones and their corresponding results.
- A spellchecker is available to correct the ouput of the OCR tool, as an option. 
- French is supported through OCR and spellchecking, as an option. 


## Handwritten Text Recognition

In order to recognize text across any kind of document, I use [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR). 

## Spellchecking
For the spellchecking I use `pyspellchecker`. I choose it because it is one of the fastest Python libraries to do it and it supports multiple langages (and even custom dictionnaries of words, which can be useful in the context of automatic grading). 
It uses the Levenshtein Distance algorithm to find words within a distance of 2. Which means it will try all different permutations and take those that exist in a dictionary as candidates for the correction. It will then select the most frequent one in the selected language as correction. 

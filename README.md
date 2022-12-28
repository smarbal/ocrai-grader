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


## Handwritten Text Recognition

In order to recognize text across any kind of document, I use [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR). 


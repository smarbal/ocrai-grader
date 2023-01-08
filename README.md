# OCRai
Automatic grader web application using AI OCR buit with Flask, Tailwind CSS + Flowbite and PaddleOCR.

![image](https://user-images.githubusercontent.com/35641452/211175562-b359498a-6327-4d6b-8b4e-7e2e0c4a164e.png)

## Installation 

Run
`sudo docker-compose -up --build` in the root directory.  
The web page will be available at http://localhost:3000/.

## Features
- Users can upload files from storage or directly take a picture with their device.
- Images can be previewed and cropped before analysis.
- PDF files can be uploaded but can't be previewed or cropped. 
- PDF files with multiple pages are also supported. 
- History of processed files is available. 
- Results for any processed are viewable. 
- PNG or JSON exports are available. The JSON will contain arrays with the coordinates of text zones and their transcription; image will directly show the zones and their corresponding results.
- A spellchecker is available to correct the ouput of the OCR tool, as an option. 
- French is supported through OCR and spellchecking, as an option. 


## Handwritten Text Recognition

In order to recognize text across any kind of document, I use [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR).
I've selected this toolkit for a few reasons : 
- Performance : It uses latest state-of-the-art algorithms that have great results with great performance. 
- Ease of use : Installation is easy to do and the API is pretty simple. A few lines of code are enough to produce results with detection and recognition. 
- Open-sourced : Everything is open-sourced and written in Python. The models are also open-sourced, so it's possible to start with any of them and build upon them. This is interesting if needed for a specific use-case (e.g. handwitten text recognition).
- Multi-language OCR : This is an interesting feature, specially knowing that french text would probably be used for testing it.  

When booting the Docker container, the latest version of their model (PPOCR-v3) is automatically downloaded why the flask server. 

### Working 
![image](https://user-images.githubusercontent.com/35641452/211176906-317cadd2-d6bb-4e7e-b9cc-f26e80b33a9c.png)

The core framework of PP-OCR contains three modules: text detection,
detection frame correction, and text recognition.
- Text detection module: This module is used to detect the various text areas in the image. It has been trained on the DB (Differentiable Binarization) algorithm.
-  Detection frame correction module: To prepare for text recognition, the irregular text box is corrected into a rectangular frame and the
text direction will be judged and corrected. For example, it can perform rotations to have a straight text. This relies on training a text direction classifier.
- Text recognition module: Finally, the module performs text recognition on the corrected detected box to obtain the content of the text. PP-OCR is trained on a CRNN algorithm.

Since recognition is the most important part here, I'll go in to a bit more detail : 
Convolutional Recurrent Neural Network use a combination of convolutional neural networks (CNNs) and recurrent neural networks (RNNs) to process the images.
- The CNN is good at extracting the features from the images. There is a large amount of contextual information in the input data when doing OCR. The goal of the CNN) is to focus on local information, so it is difficult to take account of the context by only using CNN. To solve this problem,  a bidirectional LSTM (Long Short-Term Memory) is introduced to enhance the context modeling, which has been proven in various projects. 
- The ouputput of the CNN is fed into the RNN, which processes sequential data. It allows to better capture the context (and therefore better predict abiguous characters), process texts of any length and propagate errors back to the CNN. 

![image](https://user-images.githubusercontent.com/35641452/211216951-0b0ad608-cf7a-417e-9a76-886f8981c6ef.png)

### Drawbacks
It is a Chinese project; developemnt and documentation seems geared towards the Chinese community : the chat platform is WeChat (popular Chinese communication app) and a few pre-trained models are Chinese only (handtext recognition model exists for Chinese but not English). 

### Finetuned model 

I finetuned the latest, best performing model (PPOCR-v3) to specialize in handwritten text recognition. I followed the official [documentation](https://github.com/PaddlePaddle/PaddleOCR/blob/release%2F2.6/doc/doc_en/recognition_en.md#21-start-training) to train my model on the [IAM dataset](https://fki.tic.heia-fr.ch/databases/iam-handwriting-database). The project offers a simple API to train or re-train your models. 
The main steps were : 
1. Setting a training and a validation set. 
2. Format my labels correctly and convert them to be compatible with PaddleOCR.
3. Configure the `yml` configuration file. This is done from a available template, I mostly had to configure my pre-trained model name, my data files name and the learning rate. 
4. Use PaddleOCR training tool with the configuration file to start the training. 

The configuration files can be found on `./train`. 
That model is finally not included because the initial one wasn't having good results (bad generalisation) and GPU driver problems made it impossible to train it again. 

## Spellchecking
For the spellchecking I use `pyspellchecker`. I choose it because it is one of the fastest Python libraries to do it and it supports multiple langages (and even custom dictionnaries of words, which can be useful in the context of automatic grading).  

It uses the Levenshtein Distance algorithm to find words within a distance of 2. Which means it will try all different insertions, deletions, and substitutions (with a maximum of 2 operations) and compare the results to a dictionary. If the words exist, they are taken as candidates for the correction. It will then select the most frequent one amongst the ones with the smallest distance in the selected language as correction. 

Other libraries were available such as TextBlob (which is used for a wider application range) that use AI but I was having mixed results. 
Solutions such as ChatGPT were really good at correcting texts, even with a lot of errors, but I wanted to use open-sourced tools and have everything necessary contained in this repository.  

## Sources
- https://paddleocr.bj.bcebos.com/ebook/Dive_into_OCR.pdf
- https://learnopencv.com/optical-character-recognition-using-paddleocr/
- https://github.com/PaddlePaddle/PaddleOCR
- https://fki.tic.heia-fr.ch/databases/iam-handwriting-database

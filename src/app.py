from flask import Flask, request, Response, render_template, flash, redirect, url_for, session
from paddleocr import PaddleOCR,draw_ocr
import cv2
import matplotlib.pyplot as plt
from werkzeug.utils import secure_filename
import subprocess
import re
import os
import numpy as np
import cv2
from PIL import Image

from flask_cors import CORS

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

UPLOAD_FOLDER = './images'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])




ocr = PaddleOCR(use_angle_cls=True, lang='en') # need to run only once to download and load model into memory



# draw result

app = Flask(__name__)
CORS(app)
app.secret_key = 'ThisIsaSecret'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/analyze", methods=["POST"])
def analyze(): 
    
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    file = request.files['file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        flash('No selected file')
        # return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(img_path)
        ################################################################
        # read
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

        # increase contrast
        pxmin = np.min(img)
        pxmax = np.max(img)
        imgContrast = (img - pxmin) / (pxmax - pxmin) * 255

        # increase line width
        kernel = np.ones((3, 3), np.uint8)
        imgMorph = cv2.erode(imgContrast, kernel, iterations = 1)

        # write
        cv2.imwrite(img_path + 'preprocessed.png', imgMorph)
        ################################################################
        result = analyze_paddle(img_path + 'preprocessed.png')
        output = subprocess.getoutput(f"cd HTR/SimpleHTR/src/ && python main.py --img_file ../../../{img_path}") # --decoder wordbeamsearch
        # Use REGEX to extract output information without tensorflow warnings
        recognized = re.findall(r'Recognized: "(.*?)"', output)
        probability = re.findall(r'Probability: .*', output)
        flash(output)
        ""
        return result

# def analyze(): 
    
#     # check if the post request has the file part
#     if 'file' not in request.files:
#         flash('No file part')
#         return redirect(url_for('index'))
#     file = request.files['file']
#     # if user does not select file, browser also
#     # submit a empty part without filename
#     if file.filename == '':
#         flash('No selected file')
#         # return redirect(request.url)
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(img_path)
#         output = subprocess.getoutput(f"cd HTR/SimpleHTR/src/ && python main.py --img_file ../../../{img_path}") # --decoder wordbeamsearch
#         # Use REGEX to extract output information without tensorflow warnings
#         recognized = re.findall(r'Recognized: "(.*?)"', output)
#         probability = re.findall(r'Probability: .*', output)
#         flash(output)
#         ""
#         return output


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def analyze_paddle(img_path): 
    result = ocr.ocr(img_path, cls=True)
    result = result[0]
    image = Image.open(img_path).convert('RGB')
    boxes = [line[0] for line in result]
    txts = [line[1][0] for line in result]
    scores = [line[1][1] for line in result]
    im_show = draw_ocr(image, boxes, txts, scores, font_path='./fonts/simfang.ttf')
    im_show = Image.fromarray(im_show)
    im_show.save(img_path +  '_result.jpg')
    return result


if __name__ == '__main__':
    app.debug = True
    app.run()
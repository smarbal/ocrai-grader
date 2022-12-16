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

UPLOAD_FOLDER = './static/images'
UPLOAD_FOLDER_RESULT = './static/result_images'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])




ocr = PaddleOCR(use_angle_cls=True, lang='en') # need to run only once to download and load model into memory



# draw result

app = Flask(__name__)
CORS(app)
app.secret_key = 'ThisIsaSecret'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER_RESULT'] = UPLOAD_FOLDER_RESULT

    


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
        #preprocess(img_path)
        ################################################################
        if filename.rsplit('.', 1)[1].lower() == 'pdf' : 
            result = analyze_paddle_pdf(img_path)
        else :
            result = analyze_paddle(img_path)
        
        draw_box(filename, result)
        format_result(result)
        ################################################################
        #Use SimpleHTR 
        # output = subprocess.getoutput(f"cd HTR/SimpleHTR/src/ && python main.py --img_file ../../../{img_path}") # --decoder wordbeamsearch
        # # Use REGEX to extract output information without tensorflow warnings
        # recognized = re.findall(r'Recognized: "(.*?)"', output)
        # probability = re.findall(r'Probability: .*', output)
        # flash(output)                   
        ################################################################
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

def preprocess(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

    # increase contrast
    pxmin = np.min(img)
    pxmax = np.max(img)
    imgContrast = (img - pxmin) / (pxmax - pxmin) * 255

    # increase line width
    kernel = np.ones((3, 3), np.uint8)
    imgMorph = cv2.erode(imgContrast, kernel, iterations = 1)

    # write
    cv2.imwrite(img_path, imgMorph)
    
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def draw_box(filename, result):
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image = Image.open(img_path).convert('RGB')
    boxes = [line[0] for line in result]
    txts = [line[1][0] for line in result]
    scores = [line[1][1] for line in result]
    im_show = draw_ocr(image, boxes, txts, scores, font_path='./fonts/simfang.ttf')
    
    filename = filename.rsplit('.', 1)[0] + '_result.' + filename.rsplit('.', 1)[1]
    img_path = os.path.join(app.config['UPLOAD_FOLDER_RESULT'], filename)
    im_show = Image.fromarray(im_show)
    im_show.save(img_path)

def analyze_paddle(img_path): 
    result = ocr.ocr(img_path, cls=True)
    result = result[0]
    return result

def format_result(result):
    full = ''
    for elem in result :
        full += elem[1][0]
    result.append(full)

def analyze_paddle_pdf(pdf_path):
    # Paddleocr supports Chinese, English, French, German, Korean and Japanese.
    # You can set the parameter `lang` as `ch`, `en`, `fr`, `german`, `korean`, `japan`
    # to switch the language model in order.
    
    result = ocr.ocr(pdf_path, cls=True)

    # draw result
    import fitz

    imgs = []
    with fitz.open(pdf_path) as pdf:
        for pg in range(0, pdf.pageCount):
            page = pdf[pg]
            mat = fitz.Matrix(2, 2)
            pm = page.getPixmap(matrix=mat, alpha=False)
            # if width or height > 2000 pixels, don't enlarge the image
            if pm.width > 2000 or pm.height > 2000:
                pm = page.getPixmap(matrix=fitz.Matrix(1, 1), alpha=False)

            img = Image.frombytes("RGB", [pm.width, pm.height], pm.samples)
            img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            imgs.append(img)
    for idx in range(len(result)):
        res = result[idx]
        image = imgs[idx]
        boxes = [line[0] for line in res]
        txts = [line[1][0] for line in res]
        scores = [line[1][1] for line in res]
        im_show = draw_ocr(image, boxes, txts, scores, font_path='./fonts/simfang.ttf')
        im_show = Image.fromarray(im_show)
        im_show.save('result_page_{}.jpg'.format(idx))
    return result 
if __name__ == '__main__':
    app.debug = True
    app.run()
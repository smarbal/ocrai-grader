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
import json
from flask_cors import CORS
from spellchecker import SpellChecker
from textblob import TextBlob

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

UPLOAD_FOLDER = './static/images'  
UPLOAD_FOLDER_RESULT = './static/result_images'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])




ocr = PaddleOCR(use_angle_cls=True, lang='en') # need to run only once to download and load model into memory
ocr_fr = PaddleOCR(use_angle_cls=True, lang='fr') # need to run only once to download and load model into memory
english = SpellChecker()  # the default is English (language='en')
french = SpellChecker(language='fr')  # use the French Dictionary



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
    lang = request.form['lang'] 
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
        pages = 0
        
        if filename.rsplit('.', 1)[1].lower() == 'pdf' : 
            result, pages = analyze_paddle_pdf(img_path, lang)
            format_result_pdf(result)

        else :
            result = analyze_paddle(img_path, lang)
            draw_box(filename, result)
            format_result(result)

        if request.form['spellcheck'] == 'true' :  
            spellcheck(result, lang) 
 
        save_json(filename, result, pages)
        return redirect(url_for('result', document=filename)) 
    return 'Error'


@app.route("/history", methods=["GET"])
def history(): 
    with open('static/results.json', 'r') as f:
        data = json.load(f) 
    return render_template('history.html', history=data)

@app.route("/result/<document>", methods=["GET"])
def result(document): 
    pdf = is_pdf(document)
    page = request.args.get('page', default=0, type=(int)) 
    with open('static/results.json', 'r') as f:
        data = json.load(f)
    result = data[document]['result']
    result_image = data[document]['result_img']
    return render_template('result.html', result=result, result_image=result_image, pdf=pdf, page=page,document=document)

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

def analyze_paddle(img_path, lang): 
    if lang == 'fr' : 
        result = ocr_fr.ocr(img_path, cls=True)
    else : 
        result = ocr.ocr(img_path, cls=True)
    result = result[0]
    return result


def spellcheck(result, lang):
    if lang == 'fr' : 
        checker = french
    else : 
        checker = english
    
    corrected = ''
    text = result[-1].split(' ')
    for elem in text :
        try :  
            corrected += checker.correction(elem)
        except : 
            corrected += elem
        corrected += ' '
    
    if lang == 'en' : 
        blob = TextBlob(corrected) 
        corrected = str(blob.correct())  

    result.append(corrected)




def format_result(result):
    full = ''
    for elem in result :
        full += elem[1][0]
        full += ' '
    result.append(full)
    
def format_result_pdf(result):
    for page in result :
        full = ''
        for i in page : 
            full += i[1][0]
            full += ' '
        page.append(full)

def save_json(filename, result, pages=0):
    if filename.rsplit('.', 1)[1] == 'pdf' :
        result_filenames = [filename.rsplit('.', 1)[0] + f'_result_page_{i}.jpg' for i in range(0, pages)]
        result_img_path = [os.path.join(app.config['UPLOAD_FOLDER_RESULT'], result_filename) for result_filename in result_filenames]
    else : 
        result_filename = filename.rsplit('.', 1)[0] + '_result.' + filename.rsplit('.', 1)[1]
        result_img_path = os.path.join(app.config['UPLOAD_FOLDER_RESULT'], result_filename)
        
     
    
    data={}
    data = {"result" : result,
                      "result_img" : result_img_path}

    with open("static/results.json", "r") as read_file:
        original = json.load(read_file)
        original[filename] = data
    with open("static/results.json", "w") as write_file:
        json.dump(original, write_file) 
     
def analyze_paddle_pdf(pdf_path, lang):
    # Paddleocr supports Chinese, English, French, German, Korean and Japanese.
    # You can set the parameter `lang` as `ch`, `en`, `fr`, `german`, `korean`, `japan`
    # to switch the language model in order.
    if lang == 'fr' : 
        result = ocr_fr.ocr(pdf_path, cls=True)
    else : 
        result = ocr.ocr(pdf_path, cls=True)
     

    # draw result
    import fitz

    imgs = []  
    with fitz.open(pdf_path) as pdf:
        pages = pdf.pageCount
        for pg in range(0, pdf.pageCount):
            page = pdf[pg]
            mat = fitz.Matrix(2, 2)
            pm = page.get_pixmap(matrix=mat, alpha=False)
            # if width or height > 2000 pixels, don't enlarge the image
            if pm.width > 2000 or pm.height > 2000:
                pm = page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)

            img = Image.frombytes("RGB", [pm.width, pm.height], pm.samples)
            #img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            img.save(os.path.join( app.config['UPLOAD_FOLDER'], pdf_path.split('/')[-1].split('.')[0] + '_page_{}.jpg'.format(pg)))
            imgs.append(img)
    for idx in range(len(result)):
        res = result[idx]
        image = imgs[idx]
        boxes = [line[0] for line in res]
        txts = [line[1][0] for line in res]
        scores = [line[1][1] for line in res]
        im_show = draw_ocr(image, boxes, txts, scores, font_path='./fonts/simfang.ttf')
        im_show = Image.fromarray(im_show)
        img_path = os.path.join( app.config['UPLOAD_FOLDER_RESULT'], pdf_path.split('/')[-1].split('.')[0] + '_result_page_{}.jpg'.format(idx))
        im_show.save(img_path)
    return result, pages  

def is_pdf(filename) : 
    return filename.rsplit('.', 1)[1] == 'pdf'
if __name__ == '__main__':
    app.debug = True
    app.run()
    
    


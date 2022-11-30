from flask import Flask, request, Response, render_template, flash, redirect, url_for, session
from paddleocr import PaddleOCR,draw_ocr
import cv2
import matplotlib.pyplot as plt
from werkzeug.utils import secure_filename
import subprocess
import re
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

UPLOAD_FOLDER = './images'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])




# ocr = PaddleOCR(use_angle_cls=True, lang='en') # need to run only once to download and load model into memory



# draw result

app = Flask(__name__)
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
        output = subprocess.getoutput(f"cd HTR/SimpleHTR/src/ && python main.py --img_file ../../../{img_path} --line_mode") # --decoder wordbeamsearch
        # Use REGEX to extract output informatoin without tensorflow warnings
        recognized = re.findall(r'Recognized: "(.*?)"', output)
        probability = re.findall(r'Probability: .*', output)
        flash(output)
        ""
        return output


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# result = ocr.ocr(img_path, cls=True)
# for idx in range(len(result)):
#     res = result[idx]
#     for line in res:
#         print(line)

# @app.route("/analyze", methods=["POST"])
# def analyze(): 
#     from PIL import Image
#     result = result[0]
#     image = Image.open(img_path).convert('RGB')
#     boxes = [line[0] for line in result]
#     txts = [line[1][0] for line in result]
#     scores = [line[1][1] for line in result]
#     im_show = draw_ocr(image, boxes, txts, scores, font_path='./fonts/simfang.ttf')
#     im_show = Image.fromarray(im_show)
#     im_show.save('result.jpg')
#     return 'test'

# def save_ocr(img_path, out_path, result, font):
#   save_path = os.path.join(out_path, img_path.split('/')[-1] + 'output')
 
#   image = cv2.imread(img_path)
 
#   boxes = [line[0] for line in result]
#   txts = [line[1][0] for line in result]
#   scores = [line[1][1] for line in result]
 
#   im_show = draw_ocr(image, boxes, txts, scores, font_path=font)
  
#   cv2.imwrite(save_path, im_show)
 
#   img = cv2.cvtColor(im_show, cv2.COLOR_BGR2RGB)
#   plt.imshow(img)

if __name__ == '__main__':
    app.debug = True
    app.run()
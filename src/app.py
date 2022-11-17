from flask import Flask, request, Response, render_template
from paddleocr import PaddleOCR,draw_ocr

import os

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')
FROM paddlepaddle/paddle:2.4.0rc0-cpu

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt

COPY templates templates
COPY static static
COPY images images
COPY HTR HTR

COPY package-lock.json package.json tailwind.config.js ./

COPY app.py .

RUN cd HTR/CTCWordBeamSearch && pip install .

ENV FLASK_APP=app.py

CMD ["flask", "run", "--host=0.0.0.0", "--port=3000"]

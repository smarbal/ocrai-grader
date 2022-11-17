FROM registry.baidubce.com/paddlepaddle/paddle:2.1.3-gpu-cuda10.2-cudnn7

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt

COPY templates templates
COPY static static

COPY package-lock.json package.json tailwind.config.js ./

COPY app.py .

ENV FLASK_APP=app.py

CMD ["flask", "run", "--host=0.0.0.0", "--port=3000"]

FROM python:3.10.8-bullseye

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY public public
COPY templates templates

COPY app.py .

USER 404:404

CMD ["flask", "run", "--host=0.0.0.0", "--port=3000"]

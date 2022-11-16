FROM python:3.10.8-bullseye

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY templates templates
COPY static static

COPY package-lock.json package.json tailwind.config.js ./

COPY app.py .

USER 404:404

CMD ["flask", "run", "--host=0.0.0.0", "--port=3000"]

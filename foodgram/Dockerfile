FROM python:3.7-slim

WORKDIR /foodgram

COPY . .

RUN python3 -m pip install --upgrade pip

RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000" ] 

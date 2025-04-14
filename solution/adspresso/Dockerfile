FROM python:3.12
RUN mkdir /code
WORKDIR /code
COPY . /code
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install gunicorn
RUN pip install gevent
RUN pip install natasha


EXPOSE 8080


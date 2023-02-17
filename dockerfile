FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
RUN pip install -U pip aiofiles python-multipart jinja2
RUN apt-get update \
    &&  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata
    
RUN TZ=Asia/Taipei \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata 

WORKDIR /app

COPY /api /app
COPY /static /app/static
ENV PORT 5000

CMD uvicorn app:app --host=0.0.0.0 --port=${PORT}
FROM python:3.7

WORKDIR /myproject

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY ./ ./

RUN chmod +x /myproject/script.sh

ENTRYPOINT ["/myproject/script.sh"]

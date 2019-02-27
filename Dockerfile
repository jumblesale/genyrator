FROM python:3.7

RUN mkdir /genyrator
WORKDIR /genyrator

COPY ./requirements.txt /genyrator/requirements.txt
RUN pip install -r requirements.txt

COPY . ./

CMD ["make", "test"]

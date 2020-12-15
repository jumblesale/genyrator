FROM python:3.6

RUN mkdir /genyrator
WORKDIR /genyrator

COPY . ./

RUN pip install pipenv && \
    pipenv install --dev --system

CMD ["make", "test"]

FROM python:3.6

RUN mkdir /genyrator
WORKDIR /genyrator

COPY . ./

RUN pip install pipenv && \
    pipenv sync --dev

CMD ["make", "test"]

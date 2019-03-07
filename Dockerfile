FROM python:3.6

RUN mkdir /genyrator
WORKDIR /genyrator

COPY . ./

RUN pip install pipenv && \
    pipenv install --system && \
    pipenv sync --dev

CMD ["make", "test"]

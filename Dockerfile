FROM python:3.6

RUN mkdir /genyrator
WORKDIR /genyrator

COPY . ./

RUN pip install pipenv && \
    pipenv install --system && \
    pipenv sync --dev

ENV PATH /root/.local/share/virtualenvs/genyrator-oIyKmRQj/bin:$PATH

CMD ["make", "test"]

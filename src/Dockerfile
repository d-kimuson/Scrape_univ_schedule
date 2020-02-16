FROM python:3.7.6-stretch
WORKDIR /python_app
COPY ./Pipfile /python_app/Pipfile
COPY ./Pipfile.lock /python_app/Pipfile.lock
RUN python -m pip install --upgrade pip
RUN pip install pipenv
RUN pipenv install --dev --ignore-pipfile

FROM python
LABEL maintainer="Bontchev"
COPY . /elasticpot/
WORKDIR /elasticpot
RUN pip install -r requirements.txt
CMD [ "python", "./elasticpot.py" ]


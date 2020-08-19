FROM python
LABEL maintainer="Bontchev"
LABEL name="elasticpot"
LABEL version="1.0.7"
EXPOSE 9200
COPY . /elasticpot/
WORKDIR /elasticpot
RUN pip install -r requirements.txt
CMD [ "python", "./elasticpot.py" ]

FROM python:3

RUN apt-get update && apt-get install -y git

RUN git clone https://github.com/pa-external-apis/cosmos_monitoring_1.git

WORKDIR cosmos_monitoring_1

RUN pip install -r requirements.txt

CMD [ "python3", "app.py" ]

FROM python:latest

WORKDIR /trade

COPY tradingBot.py /trade/tradingBot.py

RUN pip install --no-cache-dir requests pandas
RUN pip install ta

CMD ["python", "tradingBot.py"]


FROM python:3.10.4-alpine3.15
WORKDIR /usr/src/app
COPY . .
RUN python3.10 -m pip install -r requirements.txt
CMD [ "python3.10", "./src/bot.py"]

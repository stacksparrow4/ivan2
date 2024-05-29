FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

RUN mkdir data collated
COPY data ./data
COPY collated ./collated

COPY bot.py persona.py llm.py util.py messages.py ./

CMD python3 -u bot.py
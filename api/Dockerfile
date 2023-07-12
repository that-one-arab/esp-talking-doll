FROM python:3.9

WORKDIR .

COPY . .

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

CMD ["uvicorn", "index:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "9000"]
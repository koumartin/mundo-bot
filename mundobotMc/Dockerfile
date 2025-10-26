FROM python:3.12-trixie

WORKDIR /app
COPY . mundobotMc
RUN pip3 install -r mundobotMc/requirements.txt --no-cache-dir
ENV logFilePath /mclogs

CMD ["python3", "-m", "mundobotMc"]

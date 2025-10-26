FROM python:3.12-trixie

WORKDIR /app
COPY mundobotMc mundobotMc
RUN pip3 install -r mundobotMc/requirements.txt --no-cache-dir
ENV logFilePath=/mclogs/latest.log

CMD ["python3", "-m", "mundobotMc"]

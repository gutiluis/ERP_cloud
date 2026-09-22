FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# where files will be copied
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    netcat-openbsd=1.229-1 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# COPY <host-path> <image-path>
# copy contents of local backend/ directory into /app when the image is built
COPY backend/ .

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
# informs Docker that the container listens on the specified network ports at runtime
# TCP default port number
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

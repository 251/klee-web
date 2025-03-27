FROM python:3.13-slim-bookworm

# Install Docker dependencies
RUN apt-get update && apt-get install -y \
    docker.io \
    sudo

# Create non-root user with sudo access
RUN useradd -r worker
RUN echo "worker ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

COPY ./requirements.txt /
RUN pip install -r /requirements.txt && \
    rm /requirements.txt

WORKDIR /worker
COPY . /worker/worker

RUN flake8 --extend-ignore=E722 --max-complexity 12 .

CMD celery -A worker.worker worker --loglevel=info

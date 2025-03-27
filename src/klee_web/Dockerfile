FROM python:3.13-slim-bookworm

# Install Node.js, Ruby and other frontend tools
RUN apt-get update && apt-get install -y \
    sudo
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
RUN apt-get install -y \
    libpq-dev \
    nodejs \
    npm \
    postgresql-client \
    ruby-full
RUN npm install -g bower grunt-cli && \
    gem install sass

COPY ./requirements.txt /
RUN pip install -r /requirements.txt && \
    rm /requirements.txt

WORKDIR /kleeweb
COPY . /kleeweb

RUN DEVELOPMENT=1 ./build.sh
RUN ln -s /kleeweb/frontend/static /static

RUN rm -rf /var/lib/apt/lists/*

# For nginx static content
# TODO: Is there a way to avoid the symlink?
VOLUME /static/
# For nginx to uWSGI's socket
# TODO: The following doesn't work, we have to manually export the socket
# VOLUME /tmp

CMD ["./run.sh"]

FROM phusion/passenger-full

# Set correct environment variables.
ENV HOME /root

# Use baseimage-docker's init process.
CMD ["/sbin/my_init"]

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN rm -f /etc/service/nginx/down

RUN rm /etc/nginx/sites-enabled/default
ADD webapp.conf /etc/nginx/sites-enabled/webapp.conf
RUN mkdir /home/app/webapp
COPY --chown=app:app . /home/app/webapp
RUN apt update
RUN apt install -y python3-pip tesseract-ocr-deu poppler-utils
RUN pip install --upgrade pip
RUN pip install -r /home/app/webapp/requirements.txt
WORKDIR /home/app/webapp
RUN mkdir -p tmp
RUN mkdir -p media
RUN mkdir -p db
RUN mkdir -p /etc/my_init.d
COPY entrypoint.sh /etc/my_init.d/entrypoint.sh
RUN chmod +x /etc/my_init.d/entrypoint.sh

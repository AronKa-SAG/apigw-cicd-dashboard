FROM python:3.10-alpine as mybase

# Fixed part
WORKDIR /opt/dashboard-app
EXPOSE 8080
RUN set -e; \
	apk add --no-cache \
		gcc \
		libc-dev \
		linux-headers \
		git ;

FROM mybase as finished
# Frequently changing part
COPY . /opt/dashboard-app
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e ./utilities
RUN pip install -e ./dashboard

# RUN WSGI
CMD ["uwsgi", "app.ini"]

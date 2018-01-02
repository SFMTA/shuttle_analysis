FROM timescale/timescaledb-postgis

# Set the working directory to /app
#WORKDIR /app

# add requirements.txt for pip install
ADD pg_cron pg_cron

# add requirements.txt for pip install
ADD requirements.txt .

# add populate script to current directory
ADD populate.py .

# scripts in the docker-entrypoint-initdb.d/ directory will
# be run in alphabetical order
# will create tables upon container start up
ADD timescale-mta.sql /docker-entrypoint-initdb.d/
ADD z_pg_cron.sql .

# Set the database environment var
#ENV PGDATABASE shuttle_database

ADD ./requirements.txt .
# add python3
#RUN apt-get update && apt-get install -y python3
RUN apk add --no-cache --virtual .fetch-deps \
                git \
		build-base \
                sudo \
                make \
                util-linux-dev \
                python \
		python-dev \
                python3 \
		python3-dev \
    		py-pip

#RUN echo 'http://nl.alpinelinux.org/alpine/edge/main'  >> /etc/apk/repositories && \
#	echo 'http://nl.alpinelinux.org/alpine/edge/community'  >> /etc/apk/repositories && \
#	echo 'http://nl.alpinelinux.org/alpine/edge/testing'  >> /etc/apk/repositories && \
#	apk upgrade --update --no-cache && \
#	apk add --update --no-cache \
#		pg_cron

# Install any needed packages specified in requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

#RUN git clone https://github.com/citusdata/pg_cron.git && \
#    	cd pg_cron && \
#	export PATH=/usr/pgsql-10/bin:$PATH && \
#	make && sudo PATH=$PATH make install

RUN cd pg_cron && \
	make && sudo make install

# Copy the current directory contents into the container at /app
ADD . .

# scripts in the docker-entrypoint-initdb.d/ directory will
# be run in alphabetical order
# will create tables upon container start up
ADD a_timescale-mta.sql /docker-entrypoint-initdb.d/
ADD populate.sh /docker-entrypoint-initdb.d/
# Expose the PostgreSQL port
EXPOSE 5432


FROM timescale/timescaledb-postgis

# Set the working directory to /app
#WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . .

# scripts in the docker-entrypoint-initdb.d/ directory will
# be run in alphabetical order
# will create tables upon container start up
ADD a_timescale-mta.sql /docker-entrypoint-initdb.d/
ADD populate.sh /docker-entrypoint-initdb.d/

# Set the database environment var
#ENV PGDATABASE shuttle_database

# add python3
#RUN apt-get update && apt-get install -y python3
RUN apk add --no-cache --virtual .fetch-deps \
		gcc \
                libc-dev \
                make \
                util-linux-dev \
                python \
		python-dev \
                python3 \
		python3-dev \
    		py-pip

# Install any needed packages specified in requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

# Expose the PostgreSQL port
EXPOSE 5432


# Run populate.py when the container launches
#CMD ["psql", "-U", "postgres", "-d", "shuttle_database" "--file" "timescale-mta.sql"]
# docker run shuttledb psql -h 172.17.0.2 -U postgres --file timescale-mta.sql
#CMD ["python3", "populate.py", "--shuttles"]

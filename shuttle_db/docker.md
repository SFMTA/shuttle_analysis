# Docker

This describes the steps to getting a docker image built and run that contains a Linux alpine distribution with postgresql, timescaledb, postgis, and loads the shuttle DB schema and all the CSV data.

## Steps

* Install Docker and run it
* clone shuttle_analysis:

  ```
  C02RP8FEG8WP:sfmta aleung181$ git clone https://github.com/SFMTA/shuttle_analysis.git
  C02RP8FEG8WP:sfmta aleung181$ cd shuttle_analysis
  ```

* Build docker image -- this will take a couple of minutes. This downloads all the packages needed for the docker image and packages all the datafiles into the image itself 

  ```
  C02RP8FEG8WP:shuttle_analysis aleung181$ cd shuttle_db
  C02RP8FEG8WP:shuttle_db aleung181$ docker build -t shuttledb .
  <SNIP>
  Removing intermediate container 3cea1173913d
  Successfully built dc4e6307c61f
  Successfully tagged shuttledb:latest
  ```

* create a 'data' directory in the same directory where docker-run.sh is and add the shuttle and cnn .csv data files into the data directory:

  > note the name of the csv files

  ```
  C02RP8FEG8WP:shuttle_db aleung181$ mkdir data
  C02RP8FEG8WP:shuttle_db aleung181$ cp ~/Downloads/cnn_dim.csv data/cnn_dim.csv
  C02RP8FEG8WP:shuttle_db aleung181$ cp ~/Downloads/shuttle_three_days.csv data/shuttle_three_days.csv
  ```
  
* Stop local instances of postgres (if necessary). We want to make sure that when we connect to postgres using 'psql' we're connecting to the instance in the docker container, not the local instance.

  e.g. on MacOS:
  ```
  C02RP8FEG8WP:shuttle_db aleung181$ brew services stop postgresql
  ```
  
* Run container

  ```
  C02RP8FEG8WP:shuttle_db aleung181$ ./docker-run.sh
  1330b510e009fb47e3d32f4bd87b05a67e2f629958607cfdb475c079e6bf3447
  ```
  
* Verify that it's running

  ```
  C02RP8FEG8WP:shuttle_db aleung181$ docker container ls
  CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                    NAMES
  1330b510e009        shuttledb           "./backup_init.sh ..."   2 minutes ago       Up 3 minutes        0.0.0.0:5432->5432/tcp   relaxed_heyrovsky
  ```
  
  > note that '1330b510e009" is the container id that can be used later to 'docker exec' commands or stop the container

* Load shuttle and CNN data from .csv files into database
 
  * First get a bash shell into the container; Note that the /tmp directory is bound to the ./data directory that was created above. Any changes to ./data will be seen by the container in /tmp
  ```
  C02RP8FEG8WP:shuttle_db aleung181$ docker exec -i -t 1330b510e009 /bin/bash
  bash-4.3# ls /tmp/
  cnn_dim.csv             shuttle_three_days.csv       
  ```
  
  * Now populate CNN and shuttle data from the csv files in /tmp
  
  ```
  bash-4.3# python3 populate.py --cnn --cnn_csv /tmp/cnn_dim.csv 
  Found 0 CNNs in DB
  Loading new CNNs...
  Found 16187 new CNNs
  Skipping shuttle population
  bash-4.3# python3 populate.py --shuttles --shuttle_csv /tmp/shuttle_three_days.csv 
  Skipping CNN population
  Found 0 tech providers in DB
  Loading new tech providers...
  Found 8 new tech providers
  Saved 8 new tech providers
  ...
  ```

* Install postgres (if not already installed); needed for running 'psql' below
  ```
  C02RP8FEG8WP:shuttle_db aleung181$ brew install postgresql
  ```

* Once the data load has completed, use the 'psql' command to perform queries
 
  ```
  C02RP8FEG8WP:shuttle_db aleung181$ psql -U postgres -h localhost 
    psql (10.1, server 9.6.6)
    Type "help" for help.

    postgres=# \c shuttle_database
    psql (10.1, server 9.6.6)
    You are now connected to database "shuttle_database" as user "postgres".
    shuttle_database=# select count(*) from shuttle_locations;
      count  
    ---------
     2640290
    (1 row)

   ```
   
* Stop the container
   ```
   C02RP8FEG8WP:shuttle_db aleung181$ docker stop 1330b510e009
   ```

# Docker

This describes the steps to getting a docker image built and run that contains a Linux distribution with everything needed to run a Jupyter notebook that connects to the shuttle_database Postgres DB.

## Steps

* Install Docker and run it
* clone shuttle_analysis:

  ```
  C02RP8FEG8WP:sfmta aleung181$ git clone https://github.com/SFMTA/shuttle_analysis.git
 
  ```

* Build docker image -- this will take a couple of minutes. This downloads all the packages needed for the docker image.

  ```
  C02RP8FEG8WP:shuttle_analysis aleung181$ cd shuttle_analysis
  C02RP8FEG8WP:shuttle_db aleung181$ docker build -t shuttlenb .
  <SNIP>
  Removing intermediate container 3cea1173913d
  Successfully built dc4e6307c61f
  Successfully tagged shuttledb:latest
  ```

* Run container

  ```
  C02RP8FEG8WP:shuttle_db aleung181$ ./docker-run.sh
  1330b510e009fb47e3d32f4bd87b05a67e2f629958607cfdb475c079e6bf3447
  ```
  
* Get IP address of where the Postgres Database resides and update Jupyter notebook to this location

  TODO
  
* Verify that it's running

  ```
  
  ```
  
  > note that '1330b510e009" is the container id that can be used later to 'docker exec' commands or stop the container

   
* Stop the container
  To stop the shuttlenb container, simply ^C out.
  

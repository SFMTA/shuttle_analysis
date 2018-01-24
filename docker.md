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
  Successfully tagged shuttlenb:latest
  ```

* Run container

  ```
  C02RP8FEG8WP:shuttle_analysis aleung181$ ./docker-run.sh 
  Executing the command: jupyter notebook
  [I 00:08:49.347 NotebookApp] Writing notebook server cookie secret to /home/jovyan/.local/share/jupyter/runtime/notebook_cookie_secret
  [W 00:08:49.755 NotebookApp] WARNING: The notebook server is listening on all IP addresses and not using encryption. This is not recommended.
  [I 00:08:49.788 NotebookApp] JupyterLab alpha preview extension loaded from /opt/conda/lib/python3.6/site-packages/jupyterlab
  [I 00:08:49.788 NotebookApp] JupyterLab application directory is /opt/conda/share/jupyter/lab
  [I 00:08:49.795 NotebookApp] Serving notebooks from local directory: /home/jovyan
  [I 00:08:49.795 NotebookApp] 0 active kernels
  [I 00:08:49.796 NotebookApp] The Jupyter Notebook is running at:
  [I 00:08:49.796 NotebookApp] http://[all ip addresses on your system]:8888/?token=87b8ed25bf9985a8d94200bf9363fa6cf1165125c6fbfabb
  [I 00:08:49.796 NotebookApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
  [C 00:08:49.797 NotebookApp] 
    
     Copy/paste this URL into your browser when you connect for the first time,
     to login with a token:
         http://localhost:8888/?token=87b8ed25bf9985a8d94200bf9363fa6cf1165125c6fbfabb
  ```
  
* Open the Jupyter notebook by going to the above localhost URL.

* Get IP address of where the Postgres Database resides and update Jupyter notebook to point to this IP Address

  > Note: if the shuttle database and the shuttlenb (Jupyter notebook container) are on the same host, 'localhost' will not work. Use 'docker inspect' to determine the correct IP Address to use.
  
  ```
  C02RP8FEG8WP:shuttle_analysis aleung181$ docker inspect a5fc45998bf3 | grep IPAddress
            "SecondaryIPAddresses": null,
            "IPAddress": "172.17.0.3",
                    "IPAddress": "172.17.0.3",
  ```   
  
  Then modify the "SHUTTLE_DB_HOST" environment variable to connect to the right IP address. For example, open "shuttle_three_days.ipynb" and input the above IP Address for SHUTTLE_DB_HOST:
  
  ```
  os.environ['SHUTTLE_DB_USER'] = "postgres"
  os.environ['SHUTTLE_DB_PASSWORD'] =''
  os.environ['SHUTTLE_DB_HOST'] = "172.17.0.3"
  ```
  
  Now verify database connection by going to the Cell menu and selecting "Run All". You should see:

  ```
  conn = sfmta.db_connect()
  Connection Created
  ```
  
  At this point, you are ready to perform queries on the shuttle database!
  
  
* Stop the container
  To stop the shuttlenb container, simply ^C out.
  

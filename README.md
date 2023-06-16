# README for the application

## Before setting up the application.
I developed this project using Docker for desktop and windows CMD to test the api.
There are two ways to set up and test the application.

## First way.

### Set up the environment and the application.
Run the build.sh file. This will set up the environment and the application for use.

### Test the application.
1. (Optional) Run the querydb.sh file to check that there is nothing there. It will return a "[]".

2. Run the triggeretl.sh file. This will process the csv files and upload the derived features to the databse.

3. Run the querydb.sh file again to check that the expected features appear.

Note that the features will appear in a list respectively in the format of:
	- user_id
	- total_experiments
	- average_experiment_time
	- most_commonly_used_compounds

## Second way.

### Set up the environment and the application.
Run the following command in the directory which contains all the application files. 

`docker compose -f compose.dev.yml up --build`

### How to test/run the ETL process and how to query the database for the derived features.
1. (Optional) Run the following command to check the postgres database for existing derived features. 

`curl localhost:5000/query`

Note that it will return a "[]" since we have not populated anything in the database yet. 

2. Run the following command to trigger the ETL process.

`curl localhost:5000/etl`

It should return a message indicating the ETL process started.

3. Run the following command to query the postgres database to check if it was populated with the correct data.

`curl localhost:5000/query`

This will print out a list of the processed data in a table.
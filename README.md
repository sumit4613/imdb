# IMDB Task

- Framework used: FastAPI
- Database: PostgreSQL
- ORM: SQLAlchemy

# How to run

- Clone the repository
- Create a virtual environment
- Install the requirements, `pip install -r requirements.txt`
- Update the database credentials in `src/config.py`
- Make `start-reload.sh` executable, `chmod +x start-reload.sh`
- Start the server in reload mode, `./start-reload.sh`
    - On initial run, the database will be created and the tables will be populated with the data from the json file
- Open `http://localhost:3000/docs` in your browser

# How to run tests

- Run `pytest` in the root directory

# Scaling the application

To scale our application, we can use these approaches:

## Load Balancing

- The application can be scaled horizontally by running multiple instances of the application behind a load balancer
- The load balancer can be configured to route requests to the application instances based on the load on each instance
- The load balancer can also be configured to route requests to the application instances based on the location of the
  user

## Caching

- Since, movie data is not going to change frequently, we can cache the data in a cache server like Redis
- The cache server can be configured to expire the data after a certain time period
- The cache server can also be configured to expire the data when the data is updated in the database

## Database

- Master-slave replication can be used to scale the database
- The master database can be configured to write the data to the slave database
- The slave database can be configured to read the data from the master database
- The slave database can be configured to read the data from the cache server if the data is not present in the master
  database

# Improvements

- Since, I was out of time, I could have containerized the application using Docker to make it easier to run the
  application

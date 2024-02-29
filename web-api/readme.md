# Drill Sergeant Web API

RESTFul API service for Drill Sergeant. 

## Project objective

This service is meant to act as a an instance for
synchronization between different instances (e.g. tablet
app and desktop app) and enable automation with other
programs and tools. You'd be able to run this program on
your PC or server in-house or on the cloud.

## Setup

Open a terminal within the `/web-api` folder. Make a virtual
environment and install the required dependencies as
follows.

```
$ python3 -m venv .venv
$ . .venv/bin/activate
$ pip install -r requirements.txt
```

## Running

```
$ . .venv/bin/activate
# python3 -m flask run
```

## Testing

```
$ . .venv/bin/activate
# python3 -m pytest
```

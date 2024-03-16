# Drill Sergeant Web API

RESTFul API service for Drill Sergeant.

## Project objective

This service is meant to act as a an instance for
synchronization between different instances (e.g. tablet
app and desktop app) and enable automation with other
programs and tools. You'd be able to run this program on
your PC or server in-house or on the cloud.

## Setup, running, testing

The scripts `setup.sh`, `run.sh`, and `test.sh` are provided.

## Important notes

#### Use a HTTPS proxy

This service runs in HTTP. It must not be exposed to the internet as it is.
It must be behind some proxy that encrypts the requests with HTTPS and passes them to this service, such as
NGINX -  https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/

#### Create root user before getting the service online

This service must not be exposed to the public before sending a successful PUT request to `/v1/user/root`
to create the user with elevated priviledges.

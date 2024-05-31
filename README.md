# smart_cart_api_server
API for smart carts

## Setting Up

Ensure you have [`poetry`](https://python-poetry.org/) set up. Once that set up clone this project.

## Running Mock API Server

To run the API server mock for you to develop against simply run:
```
poetry run uvicorn smart_cart_api_server.tools.mock_server:app --reload
```
API Docs should be available here at [http:127.0.0.1:8000/docs](http:127.0.0.1:8000/docs)


## Integrating with keycloak and card readers

Add a `keycloak_config.json` to your working directory. It should look like this:
```json
{
    "server_url": "http://localhost:8080/",
    "username": "admin",
    "password": "YOUR ADMIN PASSWORD",
    "realm": "master",
    "client_id": "YOUR CLIENT",
    "client_secret":"YOUR SECRET"
}
```
Note: we do need the admin api in order to perform some of the verification.
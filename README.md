# smart_cart_api_server
API for smart carts

## Setting Up

Ensure you have [`poetry`](https://python-poetry.org/) set up. Once that set up clone this project.

## Running The Smart-Cart API Server

To run the API server mock for you to develop against simply run:
```
poetry run uvicorn smart_cart_api_server.endpoints.endpoints:app --reload --port 9090
```
API Docs should be available here at [http:127.0.0.1:9090/docs](http:127.0.0.1:9090/docs).

You will also be needing to have RMF's `api_server` and RMF running in the background.
The api server endpoint can be set via the `API_SERVER_URL` endpoint.

## Authenticating Cards via API server

By default we provide a simple csv based authentication mechanism. You need to
have a csv file called `CardId.csv`in order to be able to use it.
```
"card1", "admin", "clinic", "location2", "location3"
```

## Integrating with keycloak and card readers

Add a `keycloak_config.json` to your working directory and set `export ENABLE_KEYCLOACK=1`. It should look like this:
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
# smart_cart_api_server
API for smart carts

## Setting Up

Ensure you have [`poetry`](https://python-poetry.org/) set up. Once that is set up clone this project.

## Running The Smart-Cart API Server

To run the API server simply run:
```
poetry run uvicorn smart_cart_api_server.endpoints.endpoints:app --reload --port 9090
```
API Docs should be available here at [http:127.0.0.1:9090/docs](http:127.0.0.1:9090/docs).

You will need RMF's `api_server` and RMF running in the background.
The api server endpoint can be set via the `API_SERVER_URL` environment variable.

## Authenticating Cards via API server

By default we provide a simple csv based authentication mechanism. You need to
have a csv file called `CardId.csv`in order to be able to use it.
```
"cardid", "aactive_directory_id", "clinic", "location2", "location3"...
```
Note: If there is a change in the file, you will have to restart the server as the file is read only once. The server is stateless so this should not be much of a problem. An example `CardId.csv` is provided. If you want to change card authentication providers, then please extend the `smart_cart_api_server.models.tables.CardIdADIDTable.AbstractCardIdADIDTable` class and update `endpoints.py`.

## Integrating with keycloak and card readers

Add a `keycloak_config.json` to your working directory and set `export ENABLE_KEYCLOACK=1`. The config should look like this:
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
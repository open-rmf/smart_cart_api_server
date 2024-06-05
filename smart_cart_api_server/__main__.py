import uvicorn
from smart_cart_api_server.endpoints.endpoints import app


def main():
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9090,
    )


if __name__ == "__main__":
    main()

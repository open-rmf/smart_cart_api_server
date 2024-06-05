import argparse

import uvicorn

from smart_cart_api_server.endpoints.endpoints import app
import smart_cart_api_server.endpoints.endpoints as ep


def main():
    parser = argparse.ArgumentParser(description="Smart Cart API Server")
    parser.add_argument(
        "--host", help="Host to bind to, defaults to 0.0.0.0", default="0.0.0.0"
    )
    parser.add_argument(
        "--port",
        help="Port to bind to, defaults to 9090",
        default=9090,
    )
    parser.add_argument(
        "--rmf_api_server_url",
        help="RMF API Server URL, defaults to http://localhost:8000, may also be set with `API_SERVER_URL` env",
        default="http://localhost:8000",
    )
    args = parser.parse_args()

    if args.rmf_api_server_url:
        ep.api_server_url = args.rmf_api_server_url

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
    )


if __name__ == "__main__":
    main()

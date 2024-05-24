import asyncio
from smart_cart_api_server.controllers.robot_status import get_robot_status

async def main():
    await get_robot_status("tinyRobot1")


def start():
    asyncio.run(main())
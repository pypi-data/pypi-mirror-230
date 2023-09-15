"""Test class"""
import asyncio
from api import MirAIeAPI
from enums import AuthType

async def start():
    """Test"""
    async with MirAIeAPI(auth_type=AuthType.MOBILE, login_id="+xxxx", password="xxx") as api:
        await api.initialize()
        # for device in api.devices:
        #     print(f"Found {device.friendly_name} in {device.area_name}")

        # while True:
        #     await asyncio.sleep(5)

asyncio.get_event_loop().run_until_complete(start())

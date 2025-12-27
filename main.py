import aiohttp, os, datetime, time
import asyncio

import mariadb
from pymongo import AsyncMongoClient


required_env_vars = [
    "MONGO_URI",
    "MONGO_HEALTHCHECK_URL",
    "MARIADB_USER",
    "MARIADB_PASSWORD",
    "MARIADB_HOST",
    "MARIADB_HEALTHCHECK_URL",
]
for var in required_env_vars:
    if not os.getenv(var):
        raise EnvironmentError(f"Missing required environment variable: {var}")

mongo_client = AsyncMongoClient(os.getenv("MONGO_URI"))
mariadb_connection = mariadb.connect(
    user=os.getenv("MARIADB_USER"),
    password=os.getenv("MARIADB_PASSWORD"),
    host=os.getenv("MARIADB_HOST"),
    port=int(os.getenv("MARIADB_PORT", 3306)),
)
mariadb_cursor = mariadb_connection.cursor()

async def send_healthcheck(url: str, status: bool, ping: float):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{url}?status={'up' if status else 'down'}&ping={ping}"
        ) as resp:
            await resp.text()

async def check_mongo():
    try:
        await mongo_client.admin.command('ping')
        return True
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return False

async def check_mariadb():
    try:
        mariadb_cursor.execute("SELECT 1")
        return True
    except mariadb.Error as e:
        print(f"MariaDB connection failed: {e}")
        return False

async def main():
    while True:
        start = time.perf_counter()
        mongo_status = await check_mongo()
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        print(f"MongoDB status: {'up' if mongo_status else 'down'}" + f"  {elapsed}ms")
        try:
            await send_healthcheck(os.getenv("MONGO_HEALTHCHECK_URL"), mongo_status, elapsed)
            print("pushed mongo ok -", datetime.datetime.now())
        except Exception as e:
            print(f"Failed to send MongoDB healthcheck: {e}")
        
        start = time.perf_counter()
        mariadb_status = await check_mariadb()
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        print(f"MariaDB status: {'up' if mariadb_status else 'down'}" + f"  {elapsed}ms")
        try:
            await send_healthcheck(os.getenv("MARIADB_HEALTHCHECK_URL"), mariadb_status, elapsed)
            print("pushed mariadb ok -", datetime.datetime.now())
        except Exception as e:
            print(f"Failed to send MariaDB healthcheck: {e}")

        await asyncio.sleep(int(os.getenv("HEALTHCHECK_INTERVAL", 60))-1)

if __name__ == "__main__":
    asyncio.run(main())

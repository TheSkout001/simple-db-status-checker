import aiohttp
import os
import datetime
import time
import asyncio
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import MySQLdb
from pymongo import AsyncMongoClient

# init
mongo_client = None
mysql_connection = None
mysql_cursor = None

# Which databases to check based on environment variables
mongo_enabled = all(var in os.environ for var in [
    "MONGO_URI",
    "MONGO_HEALTHCHECK_URL",
])

mysql_enabled = all(var in os.environ for var in [
    "MARIADB_USER",
    "MARIADB_PASSWORD",
    "MARIADB_HOST",
    "MARIADB_HEALTHCHECK_URL",
])


# Initialize database clients
if mongo_enabled:
    mongo_client = AsyncMongoClient(os.getenv("MONGO_URI"))

if mysql_enabled:
    def create_mysql_connection():
        return MySQLdb.connect(
            user=os.getenv("MARIADB_USER"),
            passwd=os.getenv("MARIADB_PASSWORD"),
            host=os.getenv("MARIADB_HOST"),
            port=int(os.getenv("MARIADB_PORT", "3306")),
        )

    mysql_connection = create_mysql_connection()
    mysql_cursor = mysql_connection.cursor()

async def send_healthcheck(url: str, status: bool, ping: float):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{url}?status={'up' if status else 'down'}&ping={ping}"
        ) as r:
            resp = await r.json()
            if resp.get("ok") != True:
                raise ValueError(f"Healthcheck PUSH failed with response: {resp.get('msg')}")

async def mongodb_healthcheck():
    mongo_status = False
    if not mongo_enabled:
        return
    start = time.perf_counter()
    try:
        v = await mongo_client.admin.command('ping')
        logging.debug("MongoDB response: %s", v)
        if v.get('ok') == 1:
            mongo_status = True
    except Exception as e:
        logging.error("MongoDB connection failed: %s", e)
    finally:
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        logging.info("MongoDB status: %s  %sms", 'up' if mongo_status else 'down', elapsed)
        try:
            await send_healthcheck(os.getenv("MONGO_HEALTHCHECK_URL"), mongo_status, elapsed)
            logging.info("mongodb push success - %s", datetime.datetime.now())
        except Exception as e:
            logging.warning("Failed to send MongoDB healthcheck: %s", e)


async def mysql_healthcheck():
    mysql_status = False
    if not mysql_enabled:
        return
    start = time.perf_counter()
    try:
        # Run blocking MySQL query in thread to avoid blocking main loop
        def query():
            try:
                mysql_cursor.execute("SELECT 1")
                v = mysql_cursor.fetchone()
                logging.debug("MySQL response: %s", v)
                if v[0] == 1:
                    return True # we have to use return here to pass value out of thread
                return False
            except MySQLdb.Error as e:
                logging.error("MySQL connection failed: %s", e)
                return False
        mysql_status = await asyncio.to_thread(query)
    except Exception as e:
        logging.error("MySQL check failed: %s", e)
    finally:
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        logging.info("MySQL status: %s  %sms", 'up' if mysql_status else 'down', elapsed)
        try:
            await send_healthcheck(os.getenv("MARIADB_HEALTHCHECK_URL"), mysql_status, elapsed)
            logging.info("mysql push success - %s", datetime.datetime.now())
        except Exception as e:
            logging.warning("Failed to send MySQL healthcheck: %s", e)

async def main():
    try: 
        await mongo_client.admin.command('ping') # fixes initial connection delay
    except Exception:
        pass
    while True:
        if mongo_enabled:
            await mongodb_healthcheck()
        if mysql_enabled:
            await mysql_healthcheck()

        await asyncio.sleep(float(os.getenv("HEALTHCHECK_INTERVAL", "60")))

if __name__ == "__main__":
    asyncio.run(main())

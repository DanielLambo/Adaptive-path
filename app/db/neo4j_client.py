# app/db/neo4j_client.py
import os
from neo4j import AsyncGraphDatabase
from dotenv import load_dotenv
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASS = os.getenv("NEO4J_PASS")
NEO4J_DB   = os.getenv("NEO4J_DB", "neo4j")

_driver = None

def get_driver():
    global _driver
    if _driver is None:
        _driver = AsyncGraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASS),
            max_connection_lifetime=3600,
        )
    return _driver

async def close_driver():
    global _driver
    if _driver:
        await _driver.close()
        _driver = None

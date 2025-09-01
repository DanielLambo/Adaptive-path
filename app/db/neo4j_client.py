# app/db/neo4j_client.py
"""
Neo4j Driver Management

This module handles the lifecycle of the Neo4j async driver.
- A single driver instance is created for the application's lifetime.
- Connection logic is wrapped with a retry mechanism for robustness.
- Driver is closed gracefully on application shutdown.

Changes made:
- Standardized environment variable names for clarity.
- Added `tenacity` for exponential backoff on connection errors.
- Simplified the driver initialization logic.
"""

import os
import asyncio
from neo4j import AsyncGraphDatabase, Driver
from dotenv import load_dotenv
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

# Load environment variables from .env file
load_dotenv()

# Standardized environment variable names
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# Global variable to hold the single driver instance
_driver: Driver | None = None


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    retry=retry_if_exception_type((OSError, asyncio.TimeoutError)),
)
def create_driver_with_retry() -> Driver:
    """
    Creates and returns a new Neo4j driver instance with retry logic.
    This function will be called by get_driver.
    """
    if not NEO4J_URI or not NEO4J_PASSWORD:
        raise ValueError("NEO4J_URI and NEO4J_PASSWORD must be set in environment.")

    return AsyncGraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD),
        max_connection_lifetime=3600,
        keep_alive=True,
    )


def get_driver() -> Driver:
    """
    Returns the singleton Neo4j driver instance, creating it if necessary.
    """
    global _driver
    if _driver is None:
        _driver = create_driver_with_retry()
    return _driver


async def close_driver():
    """
    Closes the Neo4j driver connection if it has been initialized.
    """
    global _driver
    if _driver and hasattr(_driver, "close"):
        await _driver.close()
        _driver = None
        print("Neo4j driver closed.")

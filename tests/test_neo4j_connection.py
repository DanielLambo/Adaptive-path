# tests/test_neo4j_connection.py
import pytest
import os
import asyncio
from app.db.neo4j_client import get_driver, NEO4J_URI

# Mark this test as an integration test
pytestmark = pytest.mark.integration

# Skip this test if the NEO4J_URI is not configured
# This allows running unit tests without needing a live database
requires_neo4j = pytest.mark.skipif(
    not NEO4J_URI, reason="Requires NEO4J_URI to be set for integration tests"
)

@requires_neo4j
def test_neo4j_connection():
    """
    Tests the basic connection to the Neo4j database by running a simple query.
    This is an integration test and requires a running Neo4j instance.
    """
    async def run_query():
        driver = get_driver()
        async with driver.session() as session:
            result = await session.run("RETURN 1 AS result")
            record = await result.single()
            return record["result"]

    # A better way to handle asyncio event loops in pytest
    result = asyncio.run(run_query())

    assert result == 1

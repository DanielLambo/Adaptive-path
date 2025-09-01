# app/queries.py
"""
Cypher Queries for Neo4j

This module contains async functions for querying the Neo4j database.
All queries are parameterized to prevent Cypher injection.

Changes made:
- Converted all functions to `async` to work with the async driver.
- Replaced `session.run()` with `session.execute_read()` for read-only transactions.
- Corrected type hints to use `AsyncDriver`.
- Ensured database name is passed correctly to the session.
"""

from typing import List, Dict, Any, Optional
from neo4j import AsyncDriver

# Note: The environment variable for the database name is read in the neo4j_client,
# but we accept it as a parameter here for flexibility.


async def get_kp_by_id(
    driver: AsyncDriver, kp_id: int, db: str
) -> Optional[Dict[str, Any]]:
    """Fetches a single Knowledge Point by its ID."""
    async with driver.session(database=db) as session:
        result = await session.execute_read(
            lambda tx: tx.run(
                """
                MATCH (k:KP {id: $id})
                RETURN k.id AS id, k.name AS name, k.difficulty AS difficulty
                """,
                id=kp_id,
            ).single()
        )
        return result.data() if result else None


async def prereqs_for(driver: AsyncDriver, kp_id: int, db: str) -> List[Dict[str, Any]]:
    """Fetches all direct prerequisites for a given Knowledge Point."""
    async with driver.session(database=db) as session:
        result = await session.execute_read(
            lambda tx: tx.run(
                """
                MATCH (pre:KP)-[:PREREQUISITE_OF]->(k:KP {id: $id})
                RETURN pre.id AS id, pre.name AS name, pre.difficulty AS difficulty
                ORDER BY pre.difficulty ASC, pre.name ASC
                """,
                id=kp_id,
            ).list()
        )
        return [r.data() for r in result]


async def downstream_kps(
    driver: AsyncDriver, kp_id: int, db: str
) -> List[Dict[str, Any]]:
    """Fetches all downstream Knowledge Points (1 or 2 hops away)."""
    async with driver.session(database=db) as session:
        result = await session.execute_read(
            lambda tx: tx.run(
                """
                MATCH (k:KP {id: $id})-[:PREREQUISITE_OF*1..2]->(next:KP)
                RETURN DISTINCT next.id AS id, next.name AS name, next.difficulty AS difficulty
                ORDER BY next.difficulty ASC, next.name ASC
                """,
                id=kp_id,
            ).list()
        )
        return [r.data() for r in result]

from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

URI = os.environ["NEO4J_URI"]
AUTH = (os.environ["NEO4J_USER"], os.environ["NEO4J_PASS"])
DB = os.getenv("NEO4J_DB", "neo4j")

KPS = [
    {"id": 1, "name": "Variables & Data Types", "difficulty": 1},
    {"id": 2, "name": "Control Structures (if/else)", "difficulty": 1},
    {"id": 3, "name": "Loops (for/while)", "difficulty": 2},
    {"id": 4, "name": "Functions", "difficulty": 2},
    {"id": 5, "name": "Lists & Dictionaries", "difficulty": 2},
    {"id": 6, "name": "Recursion", "difficulty": 3},
    {"id": 7, "name": "Object-Oriented Programming", "difficulty": 3},
    {"id": 8, "name": "File Handling", "difficulty": 2},
]

PREREQS = [(1, 2), (1, 3), (2, 3), (3, 4), (1, 5), (5, 6), (4, 7), (1, 8)]


def load_kps():
    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver.session(database=DB) as s:
        # constraints: id unique, name unique
        s.run("CREATE CONSTRAINT kp_id IF NOT EXISTS FOR (k:KP) REQUIRE k.id IS UNIQUE")
        s.run(
            "CREATE CONSTRAINT kp_name IF NOT EXISTS FOR (k:KP) REQUIRE k.name IS UNIQUE"
        )

        # load nodes
        for kp in KPS:
            s.run(
                """
                MERGE (k:KP {id: $id})
                SET k.name = $name, k.difficulty = $difficulty
            """,
                kp,
            )

        # load edges
        for a, b in PREREQS:
            s.run(
                """
                MATCH (src:KP {id:$a}), (tgt:KP {id:$b})
                MERGE (src)-[:PREREQUISITE_OF]->(tgt)
            """,
                {"a": a, "b": b},
            )

    driver.close()
    print("Loaded Unit 4 KPs into Neo4j.")


if __name__ == "__main__":
    load_kps()

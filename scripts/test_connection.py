import os
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Force load .env from project root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

uri = os.environ["NEO4J_URI"]
user = os.environ["NEO4J_USER"]
password = os.environ["NEO4J_PASS"]
database = os.environ.get("NEO4J_DB", "neo4j")

driver = GraphDatabase.driver(uri, auth=(user, password))

with driver.session(database=database) as session:
    result = session.run("RETURN 'Aura Connected!' AS msg")
    print(result.single()["msg"])
driver.close()
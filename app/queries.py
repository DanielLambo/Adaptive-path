from typing import List, Dict, Any, Optional
from neo4j import Driver

def get_kp_by_id(driver: Driver, kp_id: int, db: str) -> Optional[Dict[str,Any]]:
    with driver.session(database=db) as s:
        rec = s.run("""
            MATCH (k:KP {id:$id})
            RETURN k.id AS id, k.name AS name, k.difficulty AS difficulty
        """, {"id": kp_id}).single()
        return rec.data() if rec else None

def prereqs_for(driver: Driver, kp_id: int, db: str) -> List[Dict[str,Any]]:
    with driver.session(database=db) as s:
        res = s.run("""
            MATCH (pre:KP)-[:PREREQUISITE_OF]->(k:KP {id:$id})
            RETURN pre.id AS id, pre.name AS name, pre.difficulty AS difficulty
            ORDER BY pre.difficulty ASC, pre.name ASC
        """, {"id": kp_id})
        return [r.data() for r in res]

def downstream_kps(driver: Driver, kp_id: int, db: str) -> List[Dict[str,Any]]:
    with driver.session(database=db) as s:
        res = s.run("""
            MATCH (k:KP {id:$id})-[:PREREQUISITE_OF*1..2]->(next:KP)
            RETURN DISTINCT next.id AS id, next.name AS name, next.difficulty AS difficulty
            ORDER BY next.difficulty ASC, next.name ASC
        """, {"id": kp_id})
        return [r.data() for r in res]

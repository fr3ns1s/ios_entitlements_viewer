from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
from typing import List
from pydantic import BaseModel
from typing import Optional
import os

DATA_ROOT = "data"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE = "entitlements.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

class IOSVersion(BaseModel):
    id: int
    version: str

class Process(BaseModel):
    id: int
    name: str

class ProcessDetail(BaseModel):
    path: str
    entitlements_xml: str

def list_ios_versions():
    versions = []
    for name in os.listdir(DATA_ROOT):
        path = os.path.join(DATA_ROOT, name)
        if os.path.isdir(path) and os.path.exists(os.path.join(path, "entitlements.db")):
            versions.append(name)
    return sorted(versions, reverse=True)

def get_conn_for_version(version):
    db_path = os.path.join(DATA_ROOT, version, "entitlements.db")
    if not os.path.exists(db_path):
        raise Exception(f"DB non trovato per versione {version}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/ios_versions")
def ios_versions():
    return list_ios_versions()

@app.get("/processes/{version}")
def get_processes(version: str):
    conn = get_conn_for_version(version)
    c = conn.cursor()
    c.execute("SELECT id, name FROM processes ORDER BY name")
    rows = c.fetchall()
    conn.close()
    return [{"id": r["id"], "name": r["name"]} for r in rows]

@app.get("/process/{version}/{process_id}")
def get_process(version: str, process_id: int):
    conn = get_conn_for_version(version)
    c = conn.cursor()
    c.execute("SELECT path, entitlements_xml FROM processes WHERE id = ?", (process_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return {"error": "Processo non trovato"}
    return {"path": row["path"], "entitlements_xml": row["entitlements_xml"]}


@app.get("/search_by_key")
def search_keys(key: str, version: str):
    conn = get_conn_for_version(version)
    c = conn.cursor()
    search_string = f"<key>{key}</key>"
    c.execute("SELECT id, name, path FROM processes WHERE entitlements_xml LIKE ?", (f"%{search_string}%",))
    results = [{"id": row[0], "name": row[1], "path": row[2]} for row in c.fetchall()]
    return results

@app.get("/keys_autocomplete", response_model=List[str])
def keys_autocomplete(version: str, key: str):
    conn = get_conn_for_version(version)
    c = conn.cursor()
    like_q = "%" + key + "%"
    c.execute("""
        SELECT key FROM keys
        WHERE key LIKE ?
        ORDER BY key
    """, (like_q,))
    rows = c.fetchall()
    conn.close()
    return [row["key"] for row in rows]

@app.get("/stats/{version}")
def get_stats(version: str):
    conn = get_conn_for_version(version)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM processes")
    processes_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM keys")
    keys_count = c.fetchone()[0]
    conn.close()
    return {
        "version": version,
        "processes_count": processes_count,
        "keys_count": keys_count
    }
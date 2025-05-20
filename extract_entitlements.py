import os
import sqlite3
import subprocess
import plistlib
import sys
import xml.dom.minidom

BINARIES_DIR = ""
IOS_VERSION = ""
ROOT_FOLDER = "data"

def create_open_db():
    path_version = os.path.join(ROOT_FOLDER, IOS_VERSION)
    if not os.path.exists(path_version):
        os.makedirs(path_version)
    conn = sqlite3.connect(os.path.join(path_version, "entitlements.db"))
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS processes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            path TEXT UNIQUE,
            entitlements_xml TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE
        )
    """)
    conn.commit()
    return conn

def pretty_print_xml(xml_str):
    try:
        dom = xml.dom.minidom.parseString(xml_str)
        pretty_xml_as_str = dom.toprettyxml(indent="  ")
        return pretty_xml_as_str
    except Exception as e:
        print(f"Errore nel pretty print XML: {e}")
        return xml_str
    
def run_codesign_entitlements(path):
    try:
        result = subprocess.run(
            ["codesign", "-d", "--entitlements", ":-", path],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return None

def parse_entitlements_xml(xml_text):
    try:
        plist = plistlib.loads(xml_text.encode('utf-8'))
        return plist
    except Exception as e:
        print(f"Errore parsing plist per un file: {e}")
        return None

def main():
    conn = create_open_db()
    c = conn.cursor()
    for root, dirs, files in os.walk(BINARIES_DIR):
        for file in files:
            full_path = os.path.join(root, file)

            ent_xml = run_codesign_entitlements(full_path)
            if not ent_xml:
                continue
            
            ent_xml = pretty_print_xml(ent_xml) 
            
            entitlements = parse_entitlements_xml(ent_xml)
            if entitlements is None:
                continue
            
            rel_path = os.path.relpath(full_path, BINARIES_DIR)
            if not rel_path.startswith('/'):
                rel_path = '/' + rel_path
    
            c.execute("""
                INSERT OR IGNORE INTO processes (name, path, entitlements_xml)
                VALUES (?, ?, ?)
            """, (file, rel_path, ent_xml))
            conn.commit()
            for key in entitlements:
                c.execute("INSERT OR IGNORE INTO keys (key) VALUES (?)", (key,))
                conn.commit()
    conn.close()
    print("Done!")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Error: Please provide 2 parameters.")
        print("Usage: python extractor.py <root_folder> <ios_version>")
        sys.exit(1)
    BINARIES_DIR = sys.argv[1]
    IOS_VERSION = sys.argv[2]
    main()
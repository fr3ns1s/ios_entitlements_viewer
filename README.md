# iOS Entitlements Viewer

A lightweight web-based tool to explore iOS executables and their entitlements.

> ✅ A free and open-source alternative to Jonathan Levin's (now offline) entitlement database.

---

## Features

- 🔍 **View entitlements** for executables extracted from any iOS version
- 🧩 **Filter by process** name or by **entitlement key**
- 📦 Simple, self-contained setup using:
  - Python + Uvicorn (FastAPI)
  - Bootstrap + jQuery (frontend)
- 💾 SQLite database for fast queries
- 🛠️ CLI tool to parse and import binaries using `codesign`

---

## Requirements

- Python 3.8+
- macOS (required for `codesign`)
- Linux (you can use `ldid` as an alternative changing parameters on `run_codesign_entitlements` function in `extract_entitlements.py`)
- `pip install -r requirements.txt`

---

## Usage

### 1. Extract entitlements from binaries

```bash
python3 extract_entitlements.py /path/to/executables [iOS_version]
```
Example:
```bash:
python3 extract_entitlements.py /Volumes/CrystalD22D72.D53gD53pOS/ 17.0
```

### 2. Start the web server
Run the FastAPI server with:
```bash
uvicorn main:app --reload
```
Then open index.html

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/ios_versions` | List all available iOS versions with extracted data |
| GET | `/processes/{version}` | List all processes for a given iOS version |
| GET | `/process/{version}/{process_id}` | Get details (name, path, entitlements) for a specific process |
| GET | `/keys_autocomplete` | Autocomplete entitlement keys (`version` and `q` params required) |
| GET | `/search_by_key` | Return processes that contain a given entitlement key |
| GET | `/stats/{version}` | Return number of processes and unique keys for the given iOS version |

## License

This project is licensed under the MIT License.  
See the `LICENSE` file for more details.

## Credits

Developed by Francesco Pompili  
Inspired by the work of Jonathan Levin (@Morpheus_____)  
View the original (now inactive) site: [https://newosxbook.com/ent.php](https://newosxbook.com/ent.php)







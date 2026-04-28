# eSnse — Setup & Getting Started Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Server](#running-the-server)
5. [Testing Basic Endpoints](#testing-basic-endpoints)
6. [Importing Postman Collection](#importing-postman-collection)
7. [Sample Requests & Responses](#sample-requests--responses)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you start, ensure you have:

- **Python 3.10+** installed
  ```bash
  python --version  # Should show 3.10+
  ```

- **pip** (Python package manager)
  ```bash
  pip --version
  ```

- **Git** (optional, for cloning)
  ```bash
  git --version
  ```

- **Postman** or **curl** (for testing)
  - **Postman:** [Download here](https://www.postman.com/downloads/)
  - **curl:** Pre-installed on Mac/Linux; [for Windows](https://curl.se/windows/)

---

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/KrishnSinghIITM/eSnse.git
cd eSnse
```

Or download the ZIP directly from GitHub.

### Step 2: Create Virtual Environment

```bash
# Create venv
python -m venv .venv

# Activate it
# On Mac/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

You should see `(.venv)` in your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Pydantic (data validation)
- google-genai (Gemini API client)
- python-dotenv (.env file support)
- orjson (fast JSON serialization)
- pytest (testing)

---

## Configuration

### Step 1: Get a Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key to clipboard
4. Keep it secret! Don't share it in repos.

### Step 2: Create `.env` File

In the project root (same level as `README.md`), create a file named `.env`:

```bash
touch .env
```

Add the following (replace `YOUR_KEY_HERE` with your actual key):

```env
GEMINI_API_KEY=YOUR_KEY_HERE
DATABASE_URL=app/data/finance.db
DEBUG=True
```

**Example `.env`:**
```env
GEMINI_API_KEY=AIzaSyD1234567890abcdefghijklmnopqrstuvwxyz
DATABASE_URL=app/data/finance.db
DEBUG=True
```

### Step 3: Initialize Database

The database auto-creates on first run with sample data (29 transactions):

```bash
python sample_data/seed_data.py
```

You should see:
```
Seeded 29 transactions
Created database at: app/data/finance.db
```

---

## Running the Server

### Start Development Server

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Expected output:
```
INFO:     Will watch for changes in these directories: ['/workspaces/eSnse']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Access the API

- **Live API:** `http://127.0.0.1:8000`
- **Swagger UI (interactive docs):** `http://127.0.0.1:8000/docs`
- **ReDoc (alternative docs):** `http://127.0.0.1:8000/redoc`

To stop the server: Press `Ctrl+C` in the terminal.

---

## Testing Basic Endpoints

### 1. Health Check (via curl)

```bash
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{"status":"ok"}
```

### 2. Query Endpoint (via curl)

```bash
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "question": "Show spending by category"}'
```

Expected response (with ₹ symbol):
```json
{
  "result": "Spending by category: shopping ₹1620, travel ₹585, food ₹330.75, utilities ₹300, entertainment ₹15."
}
```

### 3. Cache Stats (via curl)

```bash
curl http://127.0.0.1:8000/cache/stats
```

Expected response:
```json
{
  "size": 1,
  "keys": ["d99dfdb314a31637910b2253e8cb2307"]
}
```

---

## Importing Postman Collection

### Method 1: Import JSON File (Recommended)

1. Open **Postman**
2. Click **Import** (top-left)
3. Select **File** tab
4. Choose `postman_collection.json` from the eSnse folder
5. Click **Import**

### Method 2: Import from URL

1. Click **Import**
2. Select **Link** tab
3. Paste: `https://raw.githubusercontent.com/KrishnSinghIITM/eSnse/main/postman_collection.json`
4. Click **Continue** → **Import**

### Method 3: Manual Setup

Create a new Postman collection manually:

1. **New** → **HTTP Request**
2. Set URL to: `http://127.0.0.1:8000/query`
3. Method: **POST**
4. Body → **raw** → **JSON**
5. Paste:
   ```json
   {
     "user_id": 1,
     "question": "Show spending by category"
   }
   ```
6. Click **Send**

---

## Sample Requests & Responses

### Request 1: Average Travel Spending

**Request:**
```
POST http://127.0.0.1:8000/query
Content-Type: application/json

{
  "user_id": 1,
  "question": "Average spend on travel"
}
```

**Response:**
```json
{
  "result": "Your average spend was ₹292.50."
}
```

### Request 2: Spending by Category

**Request:**
```
POST http://127.0.0.1:8000/query
Content-Type: application/json

{
  "user_id": 1,
  "question": "Show spending by category"
}
```

**Response:**
```json
{
  "result": "Spending by category: shopping ₹1620, travel ₹585, food ₹330.75, utilities ₹300, entertainment ₹15."
}
```

### Request 3: No Data Found

**Request:**
```
POST http://127.0.0.1:8000/query
Content-Type: application/json

{
  "user_id": 1,
  "question": "How much did I spend on food last month?"
}
```

**Response (404):**
```json
{
  "message": "No transactions found"
}
```

### Request 4: Caching Demonstration

**First request (fresh):** ~25-30 seconds (Gemini API call)

```bash
time curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "question": "Show spending by category"}'
```

**Second request (cached):** ~0.002 seconds

```bash
time curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "question": "Show spending by category"}'
```

**Speedup:** 12,410x!

---

## Troubleshooting

### ❌ Issue: Port 8000 Already in Use

```
ERROR: [Errno 98] Address already in use
```

**Solution:** Kill existing processes
```bash
pkill -f "uvicorn"
```

Then restart the server.

---

### ❌ Issue: "Gemini client not installed"

```
"Gemini client not installed or not configured. Set GEMINI_API_KEY in .env to enable."
```

**Solution:**
1. Check `.env` exists in project root
2. Verify `GEMINI_API_KEY=...` is set
3. Check API key is valid (visit [Google AI Studio](https://aistudio.google.com/app/apikey))
4. Reinstall: `pip install google-genai`

---

### ❌ Issue: "LLM unavailable"

The API falls back gracefully — it still works with local heuristics!

The response comes from the fallback SQL generator, not actual errors.

---

### ❌ Issue: Database File Not Found

```
FileNotFoundError: app/data/finance.db
```

**Solution:**
```bash
python sample_data/seed_data.py
```

This creates the database and seeds 29 sample transactions.

---

### ❌ Issue: "No transactions found" on All Queries

The sample data is seeded for March-April 2026. If you're running this in a different month/year, certain timeframe queries (like "last month") may return no data.

**Solution:** Edit `sample_data/seed_data.py` to match current dates, then re-seed:
```bash
python sample_data/seed_data.py
```

---

### ❌ Issue: Module Import Errors

```
ModuleNotFoundError: No module named 'google.genai'
```

**Solution:** Ensure virtual environment is activated:
```bash
# Mac/Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate
```

Then reinstall:
```bash
pip install -r requirements.txt
```

---

## Swagger UI (Interactive Testing)

Once the server is running, visit:

### `http://127.0.0.1:8000/docs`

You can:
- ✅ See all endpoints
- ✅ Read parameter descriptions
- ✅ Try requests directly in the browser
- ✅ View response schemas

Click any endpoint → **Try it out** → Add parameters → **Execute**

---

## Architecture Overview

```
┌─────────────────────────────────────────┐
│   Client (Postman/curl/Browser)         │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  FastAPI Server (Port 8000)             │
│  - Cache Check (0.002s if hit)          │
│  - LLM Service (Gemini API)             │
│  - SQL Validator                        │
│  - SQLite Query Executor                │
│  - Response Formatter                   │
└──────────────────┬──────────────────────┘
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
    ┌────────┐ ┌────────┐ ┌────────┐
    │ Cache  │ │Gemini  │ │SQLite  │
    │Dict    │ │API     │ │DB      │
    │(in-mem)│ │        │ │        │
    └────────┘ └────────┘ └────────┘
```

---

## Next Steps

1. ✅ Install & run the server
2. ✅ Test with Postman collection
3. ✅ Explore Swagger UI at `/docs`
4. ✅ Check caching behavior (2nd request is instant!)
5. ✅ Review README.md for architecture details
6. ✅ Read code comments in `app/api/routes.py` for request flow

---

## Questions or Issues?

- 📖 See [README.md](README.md) for full documentation
- 🐛 Check [Troubleshooting](#troubleshooting) section above
- 💬 Open a GitHub issue if stuck

---

**Happy querying! 🎯**

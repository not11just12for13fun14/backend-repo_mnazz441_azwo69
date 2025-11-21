import os
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import User, Address, Activity, CatalogItem

app = FastAPI(title="Campus360 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Campus360 backend is running"}


@app.get("/test")
def test_database():
    """Connectivity and quick diagnostics"""
    response: Dict[str, Any] = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:  # noqa: BLE001
                response["database"] = f"⚠️ Connected but error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:  # noqa: BLE001
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response


# ---------- Models for simple payloads ----------
class ActivityIn(Activity):
    pass


# ---------- Activity Feed Endpoints (Unified Dashboard demo) ----------
@app.post("/api/activity", status_code=201)
def create_activity(payload: ActivityIn):
    try:
        inserted_id = create_document("activity", payload)
        return {"id": inserted_id, "ok": True}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/activity")
def list_activity(limit: int = 20):
    try:
        docs = get_documents("activity", {}, min(limit, 100))
        # Convert ObjectId to str for JSON serialization
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
        return {"items": docs}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(e))


# ---------- Demo Catalog (for cards on landing) ----------
@app.get("/api/catalog")
def list_catalog(service: Optional[str] = None, limit: int = 12):
    filt = {"service": service} if service else {}
    try:
        docs = get_documents("catalogitem", filt, min(limit, 50))
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
        return {"items": docs}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(e))


# ---------- Schema Introspection (used by tooling) ----------
@app.get("/schema")
def get_schema_definitions():
    return {
        "models": [
            "user",
            "address",
            "activity",
            "catalogitem",
        ]
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

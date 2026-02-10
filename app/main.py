from fastapi import FastAPI, HTTPException
import os
import redis

app = FastAPI()

REDIS_HOST = os.getenv("REDIS_HOST", "redis-master")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/readyz")
def readyz():
    try:
        redis_client.ping()
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="Redis not ready")

@app.get("/")
def read_root():
    value = redis_client.get("example_key")
    if value is None:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"message": value.decode()}

@app.post("/write/{key}")
def write_to_redis(key: str, value: str):
    redis_client.set(key, value)
    return {"message": f"Key '{key}' set to '{value}'"}

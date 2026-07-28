from fastapi import FastAPI, Request, Response
import json
from pyc64c.sdk import process_sdk_request

app = FastAPI(title="PYC64 Compiler Agent API")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics")
def metrics():
    return {
        "status": "healthy",
        "compiled_count": 0,
        "average_compile_time_ms": 0.0
    }

@app.post("/compile")
async def compile_api(request: Request):
    req_json = await request.json()
    res_str = process_sdk_request(json.dumps(req_json))
    res_json = json.loads(res_str)
    return res_json

import asyncio, os, secrets, time, uuid
from typing import Optional
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from aiohttp import ClientSession, ClientTimeout
from aiohttp_socks import ProxyConnector

app = FastAPI(title="Sky IP Checker")
app.mount("/static", StaticFiles(directory="static"), name="static")

API_KEY = os.getenv("SKY_API_KEY", "")
MAX_ITEMS = 1000
MAX_CONCURRENCY = 40
jobs = {}

class CheckRequest(BaseModel):
    proxies: list[str] = Field(min_length=1, max_length=MAX_ITEMS)
    protocol: str
    concurrency: int = Field(default=30, ge=1, le=MAX_CONCURRENCY)

def require_key(x_api_key: Optional[str]):
    if API_KEY and not secrets.compare_digest(x_api_key or "", API_KEY):
        raise HTTPException(status_code=401, detail="Invalid personal access key")

def parse_proxy(line: str, selected: str):
    line = line.strip()
    if not line:
        raise ValueError("Empty line")
    if "://" in line:
        scheme, rest = line.split("://", 1)
        scheme = scheme.lower()
        if scheme not in ("http", "https", "socks4", "socks5"):
            raise ValueError("Unsupported protocol")
        # HTTPS mode means test an HTTPS destination through an HTTP CONNECT proxy.
        if scheme == "https":
            scheme = "http"
        return f"{scheme}://{rest}"
    # HTTPS mode tests an HTTPS destination through a standard HTTP CONNECT proxy.
    proxy_scheme = "http" if selected == "https" else selected
    return f"{proxy_scheme}://{line}"

async def test_one(raw: str, selected: str, sem: asyncio.Semaphore):
    started = time.perf_counter()
    try:
        proxy_url = parse_proxy(raw, selected)
        async with sem:
            connector = ProxyConnector.from_url(proxy_url)
            timeout = ClientTimeout(total=9, connect=6)
            async with ClientSession(connector=connector, timeout=timeout) as session:
                async with session.get("https://api.ipify.org?format=json") as resp:
                    if resp.status != 200:
                        raise RuntimeError(f"HTTP {resp.status}")
                    data = await resp.json(content_type=None)
                    exit_ip = data.get("ip", "")
                    if not exit_ip:
                        raise RuntimeError("No exit IP returned")
        return {"proxy": raw.strip(), "status": "working",
                "response_ms": round((time.perf_counter()-started)*1000),
                "exit_ip": exit_ip, "error": ""}
    except Exception as e:
        return {"proxy": raw.strip(), "status": "dead",
                "response_ms": round((time.perf_counter()-started)*1000),
                "exit_ip": "", "error": str(e)[:120]}

async def run_job(job_id, proxies, protocol, concurrency):
    sem = asyncio.Semaphore(concurrency)
    jobs[job_id]["state"] = "running"
    jobs[job_id]["total"] = len(proxies)
    tasks = [asyncio.create_task(test_one(p, protocol, sem)) for p in proxies]
    results = []
    for task in asyncio.as_completed(tasks):
        result = await task
        results.append(result)
        jobs[job_id]["results"] = results
        jobs[job_id]["completed"] = len(results)
    jobs[job_id]["state"] = "done"

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()

@app.get("/api/health")
async def health():
    return {"ok": True, "name": "Sky IP Checker"}

@app.post("/api/jobs")
async def create_job(body: CheckRequest, x_api_key: Optional[str] = Header(default=None)):
    require_key(x_api_key)
    protocol = body.protocol.lower()
    if protocol not in ("http", "https", "socks4", "socks5"):
        raise HTTPException(400, "Choose HTTP, HTTPS, SOCKS4 or SOCKS5")
    cleaned = [p.strip() for p in body.proxies if p.strip()]
    if not cleaned:
        raise HTTPException(400, "Paste at least one proxy")
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"state": "queued", "total": len(cleaned), "completed": 0, "results": []}
    asyncio.create_task(run_job(job_id, cleaned, protocol, body.concurrency))
    return {"job_id": job_id, "total": len(cleaned)}

@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str, x_api_key: Optional[str] = Header(default=None)):
    require_key(x_api_key)
    if job_id not in jobs:
        raise HTTPException(404, "Job not found; it may have expired after a server restart")
    job = jobs[job_id]
    return {"state": job["state"], "total": job["total"],
            "completed": job["completed"], "results": job["results"]}

#!/usr/bin/env python3
"""
Fídíò Studio — Production & Local Development Smoke-Test Utility
Verifies full REST API, asynchronous queue worker, database, and storage integration.
"""

import sys
import time
import json
import urllib.request
import urllib.error

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "https://fidio.site/api/v1"
HEALTH_URL = BASE_URL.replace("/api/v1", "/healthz")

def log(msg: str, status: str = "INFO"):
    symbol = "✓" if status == "SUCCESS" else ("✗" if status == "ERROR" else "ℹ")
    print(f"[{symbol}] {msg}")

def http_post(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def http_get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def run_smoke_test():
    print("=" * 60)
    print(f"   Fídíò Studio System Integration Smoke Test")
    print(f"   Target Base URL: {BASE_URL}")
    print("=" * 60)

    # 1. Health Probe
    try:
        health_resp = http_get(HEALTH_URL)
        log(f"Health Probe Success: service='{health_resp.get('service')}' status='{health_resp.get('status')}'", "SUCCESS")
    except Exception as e:
        log(f"Health Probe Failed: {e}", "ERROR")
        sys.exit(1)

    # 2. Create Project
    try:
        proj_payload = {
            "name": f"Smoke Test Project {int(time.time())}",
            "description": "Automated system integration smoke test run",
            "aspect_ratio": "16:9"
        }
        proj_res = http_post(f"{BASE_URL}/projects", proj_payload)
        project = proj_res["data"]
        project_id = project["id"]
        log(f"Project Created Successfully: ID={project_id} name='{project['name']}'", "SUCCESS")
    except Exception as e:
        log(f"Project Creation Failed: {e}", "ERROR")
        sys.exit(1)

    # 3. Submit Generation Request
    try:
        gen_payload = {
            "prompt": "Cinematic sci-fi cityscape with flying drones and neon lights",
            "style": "cinematic",
            "aspect_ratio": "16:9",
            "target_duration_seconds": 15
        }
        gen_res = http_post(f"{BASE_URL}/projects/{project_id}/generations", gen_payload)
        job = gen_res["data"]["job"]
        job_id = job["id"]
        log(f"Generation Request Queued Successfully: JobID={job_id} status='{job['status']}'", "SUCCESS")
    except Exception as e:
        log(f"Generation Request Failed: {e}", "ERROR")
        sys.exit(1)

    # 4. Poll Job Until Completion
    log(f"Polling Job ID={job_id} until completed...")
    start_time = time.time()
    completed = False
    
    while time.time() - start_time < 30:  # Timeout 30s
        try:
            job_status_res = http_get(f"{BASE_URL}/jobs/{job_id}")
            job_data = job_status_res["data"]
            status = job_data["status"]
            stage = job_data["current_stage"]
            progress = job_data["progress_percentage"]

            log(f"Polling update: status='{status}' stage='{stage}' progress={progress}%")

            if status == "COMPLETED":
                log(f"Job Execution Completed Successfully in {round(time.time() - start_time, 2)}s!", "SUCCESS")
                completed = True
                break
            elif status == "FAILED":
                log(f"Job Execution Failed: code='{job_data.get('error_code')}' message='{job_data.get('error_message')}'", "ERROR")
                sys.exit(1)

        except Exception as e:
            log(f"Job polling query error: {e}", "ERROR")

        time.sleep(1.5)

    if not completed:
        log("Job polling timed out after 30 seconds!", "ERROR")
        sys.exit(1)

    # 5. Fetch Presigned Media Assets
    try:
        assets_res = http_get(f"{BASE_URL}/projects/{project_id}/assets")
        assets = assets_res.get("data", [])
        log(f"Retrieved {len(assets)} Media Assets with Presigned Download URLs:", "SUCCESS")
        for a in assets:
            log(f"  - Asset ID={a['id']} Type={a['asset_type']} Bucket={a['bucket_name']} URL={a.get('download_url') is not None}")
    except Exception as e:
        log(f"Media asset retrieval failed: {e}", "ERROR")
        sys.exit(1)

    print("=" * 60)
    log("ALL SYSTEM INTEGRATION SMOKE TESTS PASSED 100%!", "SUCCESS")
    print("=" * 60)

if __name__ == "__main__":
    run_smoke_test()

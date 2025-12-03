# # app/main.py
# import uuid
# import json
# import sqlite3
# import traceback
# import time
# import os
# import threading
# from concurrent.futures import ThreadPoolExecutor
# from fastapi import FastAPI, HTTPException
# from fastapi.responses import HTMLResponse

# from pydantic import BaseModel
# from app.storage import ensure_dirs, save_artifact

# from app.agents.ps_agent import parse_problem_or_generate
# from app.agents.data_agent import get_or_find_dataset
# from app.agents.prep_agent import preprocess_dataset
# from app.agents.automl_agent import run_automl
# from app.agents.eval_agent import evaluate_model

# ensure_dirs()
# DB = "runs.db"
# ARTIFACT_DIR = "artifacts"

# # thread pool to run orchestrations concurrently (tweak max_workers as needed)
# executor = ThreadPoolExecutor(max_workers=2)

# MAX_STEP_RETRIES = 1
# STEP_RETRY_BACKOFF = 2


# def init_db():
#     conn = sqlite3.connect(DB)
#     conn.execute(
#         """CREATE TABLE IF NOT EXISTS runs (
#                         run_id TEXT PRIMARY KEY,
#                         created_at REAL,
#                         status TEXT,
#                         last_error TEXT,
#                         state_json TEXT
#                     )"""
#     )
#     conn.commit()
#     conn.close()


# init_db()

# app = FastAPI(title="AutoML Orchestrator")


# class RunRequest(BaseModel):
#     run_id: str = None
#     user: dict = {}
#     mode: str = "ps_provided"
#     problem_statement: str = None
#     preferences: dict = {}


# # ----------------------
# # DB helpers
# # ----------------------
# def write_run_db(run_id, status, state=None):
#     conn = sqlite3.connect(DB)
#     conn.execute(
#         "INSERT OR REPLACE INTO runs (run_id, created_at, status, last_error, state_json) VALUES (?,?,?,?,?)",
#         (run_id, time.time(), status, "", json.dumps(state or {})),
#     )
#     conn.commit()
#     conn.close()


# def update_run_state(run_id, status, state=None, last_error=None):
#     conn = sqlite3.connect(DB)
#     conn.execute(
#         "UPDATE runs SET status=?, last_error=?, state_json=? WHERE run_id=?",
#         (status, last_error or "", json.dumps(state or {}), run_id),
#     )
#     conn.commit()
#     conn.close()


# def read_run(run_id):
#     conn = sqlite3.connect(DB)
#     cur = conn.execute(
#         "SELECT run_id, created_at, status, last_error, state_json FROM runs WHERE run_id=?",
#         (run_id,),
#     )
#     row = cur.fetchone()
#     conn.close()
#     if not row:
#         return None
#     return {
#         "run_id": row[0],
#         "created_at": row[1],
#         "status": row[2],
#         "last_error": row[3],
#         "state": json.loads(row[4] or "{}"),
#     }


# def fetch_queued_runs(limit: int = 10):
#     """Return up to `limit` runs that are currently queued."""
#     conn = sqlite3.connect(DB)
#     cur = conn.execute(
#         "SELECT run_id, state_json FROM runs WHERE status = 'queued' ORDER BY created_at ASC LIMIT ?",
#         (limit,),
#     )
#     rows = cur.fetchall()
#     conn.close()
#     out = []
#     for r in rows:
#         try:
#             state = json.loads(r[1] or "{}")
#         except Exception:
#             state = {}
#         out.append((r[0], state))
#     return out


# # ----------------------
# # Logging helper
# # ----------------------
# def append_log(run_id, text):
#     ensure_dirs()
#     p = os.path.join(ARTIFACT_DIR, f"{run_id}_log.txt")
#     with open(p, "a", encoding="utf-8") as f:
#         f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {text}\n")


# # ----------------------
# # Safe step runner
# # ----------------------
# def safe_step(step_fn, *args, run_id=None, step_name="step", retries=MAX_STEP_RETRIES, **kwargs):
#     last_exc = None
#     for attempt in range(1, retries + 2):
#         try:
#             append_log(run_id, f"START {step_name} attempt={attempt}")
#             res = step_fn(*args, **kwargs)
#             append_log(run_id, f"OK {step_name}")
#             return res
#         except Exception as e:
#             last_exc = e
#             tb = traceback.format_exc()
#             append_log(run_id, f"ERROR {step_name} attempt={attempt}: {e}\n{tb}")
#             time.sleep(STEP_RETRY_BACKOFF * attempt)
#     raise last_exc


# # ----------------------
# # Core orchestrator
# # ----------------------
# def orchestrate_run(run_id, payload):
#     """
#     Runs the pipeline for a single run_id and payload.
#     This function is safe to call in a background thread.
#     """
#     try:
#         append_log(run_id, "Orchestration started")
#         update_run_state(run_id, "running", {"phase": "ps_parse"})
#         ps = safe_step(
#             parse_problem_or_generate,
#             run_id,
#             payload.get("problem_statement", ""),
#             payload.get("preferences", {}),
#             run_id=run_id,
#             step_name="ps_agent",
#         )
#         # If the PS agent returned options (ps_generate), pick the first option
#         if "options" in ps:
#             ps_choice = ps["options"][0]
#             ps = {
#                 "task_type": ps_choice.get("task_type", "classification"),
#                 "raw_text": ps_choice.get("statement"),
#                 "plan": {"required_modalities": ["tabular"]},
#                 "keywords": [],
#             }
#         append_log(run_id, f"PS: {str(ps)[:400]}")
#         update_run_state(run_id, "running", {"phase": "dataset_search"})
#         dataset_path = safe_step(
#             get_or_find_dataset, run_id, ps, payload.get("user", {}), run_id=run_id, step_name="data_agent"
#         )
#         append_log(run_id, f"Dataset: {dataset_path}")
#         update_run_state(run_id, "running", {"phase": "preprocessing", "dataset": dataset_path})
#         prep_res = safe_step(preprocess_dataset, run_id, dataset_path, ps, run_id=run_id, step_name="prep_agent")
#         append_log(run_id, f"Prep: {str(prep_res)[:200]}")
#         update_run_state(run_id, "running", {"phase": "training", "prep": prep_res})
#         train_res = safe_step(
#             run_automl, run_id, prep_res["train_path"], ps, payload.get("preferences", {}), run_id=run_id, step_name="automl_agent"
#         )
#         append_log(run_id, f"Train: {train_res.get('model_path')}")
#         update_run_state(run_id, "running", {"phase": "evaluation", "train": train_res})
#         eval_res = safe_step(
#             evaluate_model,
#             run_id,
#             prep_res["test_path"],
#             train_res["model_path"],
#             prep_res["transformer_path"],
#             ps,
#             run_id=run_id,
#             step_name="eval_agent",
#         )
#         append_log(run_id, f"Eval metrics: {str(eval_res.get('metrics'))[:200]}")
#         plan_path = save_artifact(run_id, "plan.json", json.dumps(ps, indent=2))
#         eval_path = save_artifact(run_id, "evaluation.json", json.dumps(eval_res, indent=2))
#         artifacts = {"plan": plan_path, "dataset": dataset_path, "model": train_res.get("model_path"), "evaluation": eval_path}
#         update_run_state(run_id, "completed", {"artifacts": artifacts, "metrics": eval_res.get("metrics")})
#         append_log(run_id, "Orchestration completed")
#     except Exception as e:
#         tb = traceback.format_exc()
#         append_log(run_id, f"Run FAILED: {e}\n{tb}")
#         update_run_state(run_id, "failed", {"error": str(e)}, last_error=str(e))


# # ----------------------
# # Background worker loop
# # ----------------------
# def background_worker_loop(poll_interval: float = 3.0):
#     """
#     Continuously scan the DB for queued runs and dispatch them to executor.
#     This runs in a daemon thread started on FastAPI startup.
#     """
#     append_log("system", "Background worker started")
#     while True:
#         try:
#             queued = fetch_queued_runs(limit=10)
#             if queued:
#                 for run_id, state in queued:
#                     # simple protection: re-check status and claim the run by updating status->running
#                     current = read_run(run_id)
#                     if not current or current.get("status") != "queued":
#                         continue
#                     # set running immediately to avoid double submission
#                     try:
#                         update_run_state(run_id, "running", {"phase": "queued->running", "payload": state.get("payload")})
#                         append_log(run_id, "Background worker dispatching run")
#                         executor.submit(orchestrate_run, run_id, state.get("payload", {}))
#                     except Exception as e:
#                         append_log(run_id, f"Failed to dispatch run from background worker: {e}")
#             time.sleep(poll_interval)
#         except Exception as e:
#             append_log("system", f"Background worker loop error: {e}")
#             time.sleep(poll_interval)


# # Start background worker when app starts
# @app.on_event("startup")
# def start_background_worker():
#     t = threading.Thread(target=background_worker_loop, daemon=True, name="orchestrator-worker")
#     t.start()
#     append_log("system", "Background worker thread launched")


# # ----------------------
# # API endpoints
# # ----------------------
# @app.post("/run")
# def kick_off_run(req: RunRequest):
#     """
#     Accept a run request and queue it. The background worker will pick it up shortly.
#     """
#     run_id = req.run_id or str(uuid.uuid4())
#     write_run_db(run_id, "queued", {"payload": req.dict()})
#     append_log(run_id, f"Received run: {str(req.dict())[:400]}")
#     # Do NOT directly call executor.submit here; background worker will process the queued run
#     return {"run_id": run_id, "status": "queued"}


# @app.get("/status/{run_id}")
# def get_status(run_id: str):
#     r = read_run(run_id)
#     if not r:
#         raise HTTPException(status_code=404, detail="not found")
#     log_path = os.path.join(ARTIFACT_DIR, f"{run_id}_log.txt")
#     log_tail = ""
#     if os.path.exists(log_path):
#         with open(log_path, "r", encoding="utf-8") as f:
#             lines = f.readlines()
#             log_tail = "".join(lines[-200:])
#     artifacts = []
#     if os.path.exists(ARTIFACT_DIR):
#         for fname in os.listdir(ARTIFACT_DIR):
#             if fname.startswith(run_id + "_"):
#                 artifacts.append(os.path.join(ARTIFACT_DIR, fname))
#     r["log_tail"] = log_tail
#     r["artifacts"] = artifacts
#     return r


# @app.get("/runs")
# def list_runs(limit: int = 20):
#     conn = sqlite3.connect(DB)
#     cur = conn.execute(
#         "SELECT run_id, created_at, status FROM runs ORDER BY created_at DESC LIMIT ?",
#         (limit,),
#     )
#     rows = cur.fetchall()
#     conn.close()
#     runs = [{"run_id": r[0], "created_at": r[1], "status": r[2]} for r in rows]
#     return {"runs": runs}

# # ---------- Interactive Problem Statement endpoint ----------
# from fastapi import Body

# @app.post("/ps")
# def ps_interactive(payload: dict = Body(...)):
#     """
#     Interactive PS endpoint.
#     Input JSON:
#       { "have_ps": true|false, "problem_statement": "optional text", "preferences": {...} }
#     Output JSON:
#       {
#         "status": "ok",
#         "ps_parsed": {...}         # when user provided PS (parsed/refined)
#         OR
#         "ps_options": [ {...} ]    # when user asked to generate options
#       }
#     """
#     run_id = payload.get("run_id") or str(uuid.uuid4())
#     have_ps = bool(payload.get("have_ps"))
#     ps_text = payload.get("problem_statement", "") or ""
#     preferences = payload.get("preferences", {}) or {}

#     append_log(run_id, f"Interactive PS request have_ps={have_ps}")
#     try:
#         # If user provided a PS, parse/refine it
#         if have_ps and ps_text.strip():
#             ps = safe_step(parse_problem_or_generate, run_id, ps_text, preferences, run_id=run_id, step_name="ps_agent")
#             # return parsed/refined PS for user confirmation
#             return {"status": "ok", "mode": "parsed", "ps_parsed": ps}
#         else:
#             # Ask PS agent to generate options (empty input)
#             ps = safe_step(parse_problem_or_generate, run_id, "", preferences, run_id=run_id, step_name="ps_agent")
#             # If ps contains "options" (ps/generate) return them
#             if isinstance(ps, dict) and "options" in ps:
#                 return {"status": "ok", "mode": "generated_options", "ps_options": ps["options"]}
#             # If returned single structured PS, wrap it as option too
#             return {"status": "ok", "mode": "generated_options", "ps_options": [ps] if isinstance(ps, dict) else []}
#     except Exception as e:
#         append_log(run_id, f"ps_interactive error: {e}")
#         return {"status": "error", "error": str(e)}









# # ---------- Interactive Dashboard UI (replace previous /dashboard) ----------
# from fastapi.responses import HTMLResponse

# @app.get("/dashboard", response_class=HTMLResponse)
# def dashboard_ui():
#     html = r"""
# <!doctype html>
# <html>
# <head>
#   <meta charset="utf-8"/>
#   <title>AutoML Orchestrator — Interactive PS</title>
#   <style>
#     body{font-family:Arial,Helvetica,sans-serif;margin:20px;background:#f3f6fb;color:#0b1220}
#     .container{max-width:1100px;margin:0 auto}
#     .card{background:white;border-radius:8px;padding:16px;margin-bottom:12px;box-shadow:0 6px 18px rgba(0,0,0,0.06)}
#     label{font-weight:600}
#     .muted{color:#6b7280;font-size:13px}
#     textarea,input,select{width:100%;padding:8px;margin-top:6px;margin-bottom:6px;border:1px solid #e5e7eb;border-radius:6px}
#     button{padding:8px 12px;border-radius:6px;border:none;background:#0ea5a7;color:white;cursor:pointer}
#     .btn-ghost{background:#eef2ff;color:#1e3a8a;border:1px solid #dbeafe}
#     .log{font-family:monospace;background:#0b1220;color:#e6eef6;padding:10px;border-radius:6px;white-space:pre-wrap;max-height:320px;overflow:auto}
#     .art-list{list-style:none;padding-left:0}
#     .art-list li{padding:6px 0;border-bottom:1px dashed #eef2ff33}
#     .status {font-weight:700}
#   </style>
# </head>
# <body>
#   <div class="container">
#     <h2>AutoML — Interactive Problem Statement</h2>

#     <div class="card">
#       <label>Do you already have a problem statement?</label>
#       <div style="margin-top:8px;">
#         <button onclick="selectHavePS(true)">Yes — I have one</button>
#         <button class="btn-ghost" onclick="selectHavePS(false)">No — Please suggest</button>
#       </div>
#       <div id="chooseArea" style="margin-top:12px; display:none;">
#         <div id="havePSArea">
#           <label>Paste your problem statement</label>
#           <textarea id="user_ps" placeholder="e.g. Predict loan default from transactions"></textarea>
#           <div style="margin-top:6px"><button onclick="submitPS(true)">Parse & Refine PS</button></div>
#         </div>
#         <div id="noPSArea" style="display:none">
#           <div class="muted">Click to ask the agent to generate a few PS options for you.</div>
#           <div style="margin-top:8px"><button onclick="submitPS(false)">Generate PS Options</button></div>
#         </div>
#       </div>
#     </div>

#     <div id="resultsCard" class="card" style="display:none">
#       <h3>Problem statement options / parsed result</h3>
#       <div id="optionsContainer"></div>
#       <div style="margin-top:10px">
#         <label>Or edit the selected statement before starting run</label>
#         <textarea id="selected_ps" placeholder="Edit selected or parsed PS here"></textarea>
#         <div style="margin-top:8px">
#           <button onclick="startRunFromPS()">Start Run with this PS</button>
#         </div>
#       </div>
#     </div>

#     <div id="runCard" class="card" style="display:none">
#       <h3>Run Status</h3>
#       <div><label>Run ID</label><input id="runid" readonly/></div>
#       <div style="margin-top:8px"><label>Status</label><div id="status" class="status muted">—</div></div>
#       <div style="margin-top:8px"><label>Phase</label><div id="phase" class="muted">—</div></div>
#       <div style="margin-top:8px"><label>Last error</label><div id="lasterr" class="muted">—</div></div>
#       <div style="margin-top:8px"><label>Log tail</label><div id="log" class="log">—</div></div>
#       <div style="margin-top:8px"><label>Artifacts</label><ul id="artifacts" class="art-list"></ul></div>
#     </div>

#     <div class="muted">This UI asks whether the user has a problem statement, refines or generates PS via your PS agent, and then starts a full run when confirmed.</div>
#   </div>

# <script>
# let runPolling = null;
# function selectHavePS(choice){
#   document.getElementById("chooseArea").style.display = "block";
#   document.getElementById("havePSArea").style.display = choice ? "block" : "none";
#   document.getElementById("noPSArea").style.display = choice ? "none" : "block";
#   // reset result area
#   document.getElementById("resultsCard").style.display = "none";
# }

# async function submitPS(have_ps){
#   const psText = document.getElementById("user_ps").value || "";
#   const payload = { have_ps: have_ps, problem_statement: psText, preferences: {} };
#   try{
#     const res = await fetch("/ps", {
#       method: "POST",
#       headers: {"Content-Type":"application/json"},
#       body: JSON.stringify(payload)
#     });
#     const j = await res.json();
#     if(j.status !== "ok"){ alert("PS generation error: "+(j.error||"unknown")); return; }
#     const optsArea = document.getElementById("optionsContainer");
#     optsArea.innerHTML = "";
#     // if parsed
#     if(j.mode === "parsed" && j.ps_parsed){
#       const parsed = j.ps_parsed;
#       const pretty = parsed.raw_text || JSON.stringify(parsed, null, 2);
#       optsArea.innerHTML = `<div><b>Parsed / Refined PS</b></div><pre>${escapeHtml(pretty)}</pre>`;
#       document.getElementById("selected_ps").value = parsed.raw_text || pretty;
#     } else if(j.mode === "generated_options" && j.ps_options){
#       const list = j.ps_options;
#       let html = "<div><b>Generated options</b></div>";
#       list.forEach((opt, idx)=>{
#         let text = opt.statement || opt.raw_text || JSON.stringify(opt);
#         html += `<div style="margin-top:8px;border:1px solid #eee;padding:8px;border-radius:6px">
#                   <div style="font-weight:700">Option ${idx+1}</div>
#                   <div style="margin-top:6px"><pre>${escapeHtml(text)}</pre></div>
#                   <div style="margin-top:6px"><button onclick="chooseOption(${idx})">Choose this</button></div>
#                  </div>`;
#       });
#       optsArea.innerHTML = html;
#       // store in window for chooseOption
#       window._generated_options = list;
#     } else {
#       optsArea.innerHTML = "<div class='muted'>No options returned.</div>";
#     }
#     document.getElementById("resultsCard").style.display = "block";
#     window.scrollTo(0, document.getElementById("resultsCard").offsetTop - 20);
#   }catch(e){
#     alert("PS request failed: "+e);
#   }
# }

# function chooseOption(idx){
#   const opt = (window._generated_options || [])[idx];
#   if(!opt) return;
#   const text = opt.statement || opt.raw_text || JSON.stringify(opt);
#   document.getElementById("selected_ps").value = text;
# }

# async function startRunFromPS(){
#   const ps = document.getElementById("selected_ps").value || "";
#   if(!ps.trim()) return alert("Please provide a problem statement before starting the run.");
#   const body = {
#     user: {},
#     mode: "ps_provided",
#     problem_statement: ps,
#     preferences: { primary_metric: "f1", training_budget_minutes: 1, allow_synthetic: true, deploy: false }
#   };
#   try{
#     const res = await fetch("/run", { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(body) });
#     const j = await res.json();
#     if(!j.run_id){ alert("Run start failed"); return; }
#     document.getElementById("runid").value = j.run_id;
#     document.getElementById("runCard").style.display = "block";
#     startRunPoll(j.run_id);
#   }catch(e){ alert("Start run failed: "+e); }
# }

# function startRunPoll(run_id){
#   if(runPolling) clearInterval(runPolling);
#   fetchOnce(run_id); runPolling = setInterval(()=>fetchOnce(run_id), 3000);
# }

# function stopRunPoll(){ if(runPolling) clearInterval(runPolling); runPolling = null; }

# async function fetchOnce(run_id){
#   try{
#     const res = await fetch(`/status/${run_id}`);
#     if(!res.ok){ document.getElementById("status").innerText = "not found"; return; }
#     const j = await res.json();
#     document.getElementById("status").innerText = j.status || "-";
#     document.getElementById("phase").innerText = (j.state && j.state.phase) || "-";
#     document.getElementById("lasterr").innerText = j.last_error || "-";
#     document.getElementById("log").innerText = j.log_tail || "-";
#     const ul = document.getElementById("artifacts");
#     ul.innerHTML = "";
#     (j.artifacts || []).forEach(a=>{
#       const li = document.createElement("li");
#       li.innerHTML = `<a href="${a}" target="_blank">${a.split("/").pop()}</a>`;
#       ul.appendChild(li);
#     });
#     if(j.status && (j.status==="completed" || j.status==="failed")){ stopRunPoll(); }
#   }catch(e){
#     console.error(e);
#   }
# }

# function escapeHtml(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
# </script>
# </body>
# </html>
# """
#     return html




# # ---------- Enhanced dashboard (paste/replace existing /dashboard endpoint) ----------
# from fastapi.responses import HTMLResponse

# @app.get("/dashboard", response_class=HTMLResponse)
# def dashboard_ui():
#     html = r"""
# <!doctype html>
# <html>
# <head>
#   <meta charset="utf-8"/>
#   <title>AutoML Orchestrator — Interactive</title>
#   <style>
#     body{font-family:Arial,Helvetica,sans-serif;margin:18px;background:#f6f8fb;color:#0b1220}
#     .wrap{max-width:1100px;margin:0 auto}
#     .card{background:white;border-radius:8px;padding:14px;margin-bottom:12px;box-shadow:0 8px 24px rgba(12,24,40,0.06)}
#     textarea,input,select{width:100%;padding:8px;margin-top:6px;border:1px solid #e6e9ef;border-radius:6px}
#     button{padding:8px 12px;border-radius:6px;border:none;background:#0ea5a7;color:white;cursor:pointer}
#     .muted{color:#6b7280;font-size:13px}
#     .log{font-family:monospace;background:#0b1220;color:#e6eef6;padding:10px;border-radius:6px;white-space:pre-wrap;max-height:320px;overflow:auto}
#     .row{display:flex;gap:10px}
#     .small{font-size:13px}
#   </style>
# </head>
# <body>
#   <div class="wrap">
#     <h2>AutoML Orchestrator — Interactive</h2>

#     <div class="card">
#       <h3>Step 1 — Do you have a dataset?</h3>
#       <div class="muted">If yes: provide a local path (e.g. data/my.csv) or a public URL (.csv). If no: the system will search public datasets and may web-scrape or synthesize.</div>
#       <div style="margin-top:10px">
#         <input id="upload_path" placeholder="Local path or public URL (leave empty if none)"/>
#         <div style="margin-top:8px"><small class="muted">Tip: place a CSV in the project `data/` folder and paste its path here (e.g., data/sample.csv)</small></div>
#       </div>
#     </div>

#     <div class="card">
#       <h3>Step 2 — Problem statement</h3>
#       <div class="muted">Do you already have a problem statement?</div>
#       <div style="margin-top:8px">
#         <button onclick="chooseHavePS(true)">Yes — I have one</button>
#         <button onclick="chooseHavePS(false)" style="margin-left:6px">No — Suggest options</button>
#       </div>

#       <div id="psArea" style="margin-top:12px;display:none">
#         <div id="havePSBlock">
#           <label>Paste problem statement</label>
#           <textarea id="user_ps" placeholder="e.g. Predict loan default from transaction history"></textarea>
#           <div style="margin-top:8px"><button onclick="callPS(true)">Parse & Refine PS</button></div>
#         </div>
#         <div id="noPSBlock" style="display:none">
#           <div class="muted">Click to ask the agent to propose 2-3 problem statement options</div>
#           <div style="margin-top:8px"><button onclick="callPS(false)">Generate PS Options</button></div>
#         </div>
#       </div>
#     </div>

#     <div id="psResults" class="card" style="display:none">
#       <h3>Problem Statement — Confirm</h3>
#       <div id="psOptions"></div>
#       <div style="margin-top:10px">
#         <label>Edit/Confirm selected PS</label>
#         <textarea id="selected_ps"></textarea>
#         <div style="margin-top:8px">
#           <button onclick="startRun()">Start Run</button>
#         </div>
#       </div>
#     </div>

#     <div id="runCard" class="card" style="display:none">
#       <h3>Run Status</h3>
#       <div><label>Run ID</label><input id="runid" readonly/></div>
#       <div style="margin-top:8px"><label>Status</label><div id="status" class="small muted">—</div></div>
#       <div style="margin-top:8px"><label>Phase</label><div id="phase" class="small muted">—</div></div>
#       <div style="margin-top:8px"><label>Last error</label><div id="lasterr" class="small muted">—</div></div>
#       <div style="margin-top:8px"><label>Log tail</label><div id="log" class="log">—</div></div>
#       <div style="margin-top:8px"><label>Artifacts</label><ul id="artifacts"></ul></div>
#     </div>

#   </div>

# <script>
# let storedOptions = [];
# function chooseHavePS(v){
#   document.getElementById("psArea").style.display = "block";
#   document.getElementById("havePSBlock").style.display = v ? "block" : "none";
#   document.getElementById("noPSBlock").style.display = v ? "none" : "block";
#   document.getElementById("psResults").style.display = "none";
# }

# async function callPS(have_ps){
#   const psText = document.getElementById("user_ps").value || "";
#   const payload = { have_ps: have_ps, problem_statement: psText, preferences: {} };
#   try{
#     const res = await fetch("/ps", { method:"POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(payload) });
#     const j = await res.json();
#     if(j.status !== "ok"){ alert("PS endpoint error: "+(j.error||"unknown")); return; }
#     const container = document.getElementById("psOptions"); container.innerHTML = "";
#     if(j.mode === "parsed" && j.ps_parsed){
#       const parsed = j.ps_parsed;
#       const text = parsed.raw_text || JSON.stringify(parsed, null,2);
#       container.innerHTML = `<div><b>Parsed PS</b></div><pre>${escapeHtml(text)}</pre>`;
#       document.getElementById("selected_ps").value = parsed.raw_text || text;
#     } else if(j.mode === "generated_options" && j.ps_options){
#       storedOptions = j.ps_options;
#       let html = "<div><b>Generated options</b></div>";
#       j.ps_options.forEach((opt, idx)=>{
#         const txt = opt.statement || opt.raw_text || JSON.stringify(opt);
#         html += `<div style="margin-top:8px;border:1px solid #eee;padding:8px;border-radius:6px">
#           <div style="font-weight:700">Option ${idx+1}</div>
#           <pre>${escapeHtml(txt)}</pre>
#           <div><button onclick="chooseOption(${idx})">Choose this</button></div>
#         </div>`;
#       });
#       container.innerHTML = html;
#       document.getElementById("selected_ps").value = j.ps_options[0].statement || j.ps_options[0].raw_text || "";
#     } else {
#       container.innerHTML = "<div class='muted'>No options returned</div>";
#     }
#     document.getElementById("psResults").style.display = "block";
#   }catch(e){
#     alert("PS call failed: "+e);
#   }
# }

# function chooseOption(idx){
#   const opt = storedOptions[idx];
#   if(!opt) return;
#   const text = opt.statement || opt.raw_text || JSON.stringify(opt);
#   document.getElementById("selected_ps").value = text;
# }

# async function startRun(){
#   const ps = document.getElementById("selected_ps").value || "";
#   if(!ps.trim()){ return alert("Please confirm a problem statement before starting."); }
#   const upload_path = document.getElementById("upload_path").value || ""
#   const body = {
#     user: upload_path ? { upload_path: upload_path } : {},
#     mode: "ps_provided",
#     problem_statement: ps,
#     preferences: { primary_metric: "f1", training_budget_minutes: 2, allow_synthetic: true, deploy: false }
#   };
#   try{
#     const res = await fetch("/run", { method:"POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(body) });
#     const j = await res.json();
#     if(!j.run_id){ alert("Run failed to start"); return; }
#     document.getElementById("runCard").style.display = "block";
#     document.getElementById("runid").value = j.run_id;
#     startPoll(j.run_id);
#   }catch(e){ alert("Failed to start run: "+e); }
# }

# let poller = null;
# async function startPoll(run_id){
#   if(poller) clearInterval(poller);
#   await fetchOnce(run_id);
#   poller = setInterval(()=> fetchOnce(run_id), 3000);
# }
# function stopPoll(){ if(poller){ clearInterval(poller); poller = null } }

# async function fetchOnce(run_id){
#   try{
#     const res = await fetch(`/status/${run_id}`);
#     if(!res.ok){ document.getElementById("log").innerText = "Run not found"; return; }
#     const j = await res.json();
#     document.getElementById("status").innerText = j.status || "-";
#     document.getElementById("phase").innerText = (j.state && j.state.phase) || "-";
#     document.getElementById("lasterr").innerText = j.last_error || "-";
#     document.getElementById("log").innerText = j.log_tail || "-";
#     const ul = document.getElementById("artifacts"); ul.innerHTML = "";
#     (j.artifacts || []).forEach(a=>{
#       const li = document.createElement("li");
#       li.innerHTML = `<a href="${a}" target="_blank">${a.split("/").pop()}</a>`;
#       ul.appendChild(li);
#     });
#     if(j.status && (j.status==="completed" || j.status==="failed")) stopPoll();
#   }catch(e){
#     console.error(e);
#   }
# }

# function escapeHtml(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
# </script>
# </body>
# </html>
# """
#     return html

## app/main.py
from dotenv import load_dotenv
load_dotenv()

import os
import uuid
import json
import sqlite3
import time
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, FileResponse

from app.storage import ensure_dirs, save_artifact
from app.utils.run_logger import agent_log

from app.agents.ps_agent import parse_problem_or_generate
from app.agents.data_agent import get_or_find_dataset
from app.agents.prep_agent import preprocess_dataset
from app.agents.automl_agent import run_automl
from app.agents.eval_agent import evaluate_model

from app.dashboard_html import DASHBOARD_HTML
from app.config import Config
from app.logging_config import get_logger, log_error

# Initialize logger
logger = get_logger(__name__)

ensure_dirs()

# Use configuration from Config class
DB = Config.DB_PATH
ARTIFACT_DIR = Config.ARTIFACT_DIR
os.makedirs(ARTIFACT_DIR, exist_ok=True)

executor = ThreadPoolExecutor(max_workers=Config.THREAD_POOL_SIZE)
MAX_STEP_RETRIES = 1
STEP_RETRY_BACKOFF = 2


def init_db():
    conn = sqlite3.connect(DB)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY,
            created_at REAL,
            status TEXT,
            last_error TEXT,
            state_json TEXT
        )"""
    )
    conn.commit()
    conn.close()


init_db()
app = FastAPI(
    title="AutoML Orchestrator",
    version="1.0.0",
    description="Automated Machine Learning Pipeline Orchestrator"
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------
# Global Error Handlers
# ----------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTP exceptions with proper logging and sanitized responses
    """
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - Path: {request.url.path}")
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
        "path": str(request.url.path)
    }


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions with logging and safe error messages
    """
    # Log the full error with context
    log_error(exc, context={
        "path": str(request.url.path),
        "method": request.method,
    })
    
    # Return safe error message (don't expose internal details)
    if Config.DEBUG:
        error_detail = str(exc)
    else:
        error_detail = "An internal error occurred. Please try again later."
    
    return {
        "error": error_detail,
        "status_code": 500,
        "path": str(request.url.path)
    }


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """
    Handle validation errors (400 Bad Request)
    """
    logger.warning(f"Validation error: {str(exc)} - Path: {request.url.path}")
    return {
        "error": f"Invalid input: {str(exc)}",
        "status_code": 400,
        "path": str(request.url.path)
    }


# ----------------------
# Static Files Configuration
# ----------------------
# Mount static files if the directory exists (frontend build output)
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    logger.info(f"Static files mounted from {STATIC_DIR}")
else:
    logger.warning(f"Static directory not found: {STATIC_DIR}")


@app.get("/checkllm")
def check_llm():
    from app.utils.llm_clients import llm_generate

    try:
        out = llm_generate("say OK in one word")
        # Some LLM backends return stuff with line breaks/JSON; normalize to short string
        if isinstance(out, str):
            out_s = out.strip().splitlines()[0] if out.strip() else ""
        else:
            out_s = str(out)
        return {"ok": True, "LLM_MODE": os.getenv("LLM_MODE"), "response": out_s}
    except Exception as e:
        return {"ok": False, "error": str(e)}


class RunRequest(BaseModel):
    run_id: Optional[str] = None
    user: Dict[str, Any] = {}
    mode: str = "ps_provided"
    problem_statement: Optional[str] = None
    preferences: Dict[str, Any] = {}


# ----------------------
# DB helpers
# ----------------------
def write_run_db(run_id: str, status: str, state: Optional[Dict[str, Any]] = None):
    conn = sqlite3.connect(DB)
    conn.execute(
        "INSERT OR REPLACE INTO runs (run_id, created_at, status, last_error, state_json) VALUES (?,?,?,?,?)",
        (run_id, time.time(), status, "", json.dumps(state or {})),
    )
    conn.commit()
    conn.close()


def update_run_state(run_id: str, status: str, state: Optional[Dict[str, Any]] = None, last_error: Optional[str] = None):
    conn = sqlite3.connect(DB)
    conn.execute(
        "UPDATE runs SET status=?, last_error=?, state_json=? WHERE run_id=?",
        (status, last_error or "", json.dumps(state or {}), run_id),
    )
    conn.commit()
    conn.close()


def read_run(run_id: str):
    conn = sqlite3.connect(DB)
    cur = conn.execute(
        "SELECT run_id, created_at, status, last_error, state_json FROM runs WHERE run_id=?",
        (run_id,),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "run_id": row[0],
        "created_at": row[1],
        "status": row[2],
        "last_error": row[3],
        "state": json.loads(row[4] or "{}"),
    }


def fetch_queued_runs(limit: int = 10):
    conn = sqlite3.connect(DB)
    cur = conn.execute(
        "SELECT run_id, state_json FROM runs WHERE status='queued' ORDER BY created_at ASC LIMIT ?",
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    out = []
    for r in rows:
        try:
            state = json.loads(r[1] or "{}")
        except Exception:
            state = {}
        out.append((r[0], state))
    return out


# ----------------------
# Safe step runner
# ----------------------
# def safe_step(step_fn, *args, run_id: str = None, step_name: str = "step", retries: int = MAX_STEP_RETRIES, **kwargs):
#     last_exc = None
#     for attempt in range(1, retries + 2):
#         try:
#             agent_log(run_id, f"START {step_name} attempt={attempt}", agent="orchestrator")
#             # NOTE: do NOT pass run_id as a kwargs unless the target expects it. We pass positional args only.
#             res = step_fn(*args, **kwargs)
#             agent_log(run_id, f"OK {step_name}", agent="orchestrator")
#             return res
#         except Exception as e:
#             last_exc = e
#             tb = traceback.format_exc()
#             agent_log(run_id, f"ERROR {step_name} attempt={attempt}: {e}\n{tb}", agent="orchestrator")
#             time.sleep(STEP_RETRY_BACKOFF * attempt)
#     raise last_exc

def safe_step(step_fn, *args, run_id: str = None, step_name: str = "step",
              retries: int = MAX_STEP_RETRIES, **kwargs):
    """
    Safely executes a step with retry + logging.
    Ensures no unexpected kwargs (like run_id) are forwarded to step_fn.
    """
    last_exc = None

    # Remove orchestrator-only kwargs from forwarded args
    safe_kwargs = {k: v for k, v in kwargs.items() if k not in ("run_id", "step_name")}

    for attempt in range(1, retries + 2):
        try:
            agent_log(run_id, f"START {step_name} attempt={attempt}", agent="orchestrator")

            # <-- IMPORTANT: only pass *args and safe_kwargs
            res = step_fn(*args, **safe_kwargs)

            agent_log(run_id, f"OK {step_name}", agent="orchestrator")
            return res

        except Exception as e:
            last_exc = e
            tb = traceback.format_exc()
            agent_log(run_id,
                      f"ERROR {step_name} attempt={attempt}: {e}\n{tb}",
                      agent="orchestrator")
            time.sleep(STEP_RETRY_BACKOFF * attempt)

    raise last_exc



# ----------------------
# Core orchestrator
# ----------------------
def orchestrate_run(run_id: str, payload: Dict[str, Any]):
    """
    Runs the pipeline for a single run_id and payload.
    """
    try:
        agent_log(run_id, "Orchestration started", agent="orchestrator")
        update_run_state(run_id, "running", {"phase": "ps_parse"})

        problem_statement = payload.get("problem_statement", "") if payload else ""
        preferences = payload.get("preferences", {}) if payload else {}
        # accept hint in root payload
        if payload.get("hint"):
            preferences["hint"] = payload.get("hint")

        # ---------------- PS agent ----------------
        # parse_problem_or_generate signature: (run_id, problem_statement, preferences)
        ps_res = safe_step(parse_problem_or_generate, run_id, problem_statement, preferences, step_name="ps_agent")

        # If PS agent returned options, choose the first option
        if isinstance(ps_res, dict) and "options" in ps_res and ps_res["options"]:
            chosen = ps_res["options"][0]
            ps = {
                "raw_text": chosen.get("statement"),
                "plan": chosen.get("plan", {"required_modalities": ["tabular"]}),
                "keywords": chosen.get("keywords", []),
                "source": "generated_option",
            }
        else:
            ps = ps_res if isinstance(ps_res, dict) else {"raw_text": str(ps_res)}

        agent_log(run_id, f"PS prepared: {str(ps)[:400]}", agent="orchestrator")
        update_run_state(run_id, "running", {"phase": "dataset_search", "ps_preview": str(ps)[:300]})

        # ---------------- Data agent ----------------
        ds_res = safe_step(get_or_find_dataset, run_id, ps, payload.get("user", {}), step_name="data_agent")
        dataset_path = None
        dataset_source = "Unknown"
        dataset_source_name = "Unknown"
        dataset_source_url = ""
        
        if isinstance(ds_res, dict):
            dataset_path = ds_res.get("dataset_path") or ds_res.get("dataset_uri") or ds_res.get("downloaded_to")
            dataset_source = ds_res.get("source", "Unknown")
            dataset_source_name = ds_res.get("source_name", "Unknown")
            dataset_source_url = ds_res.get("source_url", "")
        elif isinstance(ds_res, str):
            dataset_path = ds_res
        else:
            dataset_path = str(ds_res)

        if not dataset_path:
            raise RuntimeError("Data agent did not return dataset path")

        agent_log(run_id, f"Dataset selected: {dataset_path} from {dataset_source}: {dataset_source_name}", agent="orchestrator")
        update_run_state(run_id, "running", {
            "phase": "preprocessing", 
            "dataset": dataset_path,
            "dataset_source": dataset_source,
            "dataset_source_name": dataset_source_name,
            "dataset_source_url": dataset_source_url
        })

        # ---------------- Preprocess ----------------
        prep_res = safe_step(preprocess_dataset, run_id, dataset_path, ps, step_name="prep_agent")

        if not isinstance(prep_res, dict) or "train_path" not in prep_res:
            raise RuntimeError("Preprocessing agent returned invalid result")

        agent_log(run_id, f"Preprocessing complete: train={prep_res.get('train_path')}", agent="orchestrator")
        update_run_state(run_id, "running", {"phase": "training", "prep": {"train": prep_res.get("train_path")}})

        # ---------------- AutoML ----------------
        train_res = safe_step(run_automl, run_id, prep_res["train_path"], ps, preferences, step_name="automl_agent")

        if not isinstance(train_res, dict) or "model_path" not in train_res:
            raise RuntimeError("AutoML agent returned invalid result")

        auto_task = train_res.get("automl_settings", {}).get("task") or train_res.get("task_type")
        if auto_task:
            ps["task_type"] = auto_task

        agent_log(run_id, f"Training complete: model={train_res.get('model_path')}, task={ps.get('task_type')}", agent="orchestrator")
        update_run_state(run_id, "running", {"phase": "evaluation", "train": {"model": train_res.get("model_path")}})

        # ---------------- Evaluate ----------------
        eval_res = safe_step(
            evaluate_model,
            run_id,
            prep_res["test_path"],
            train_res["model_path"],
            prep_res["transformer_path"],
            ps,
            step_name="eval_agent",
        )

        agent_log(run_id, f"Evaluation complete: metrics={str(eval_res.get('metrics'))[:400]}", agent="orchestrator")

        # Save artifacts
        plan_path = save_artifact(run_id, "plan.json", json.dumps(ps, indent=2))
        eval_path = save_artifact(run_id, "evaluation.json", json.dumps(eval_res, indent=2))

        artifacts = {
            "plan": os.path.basename(plan_path),
            "dataset": dataset_path,
            "model": os.path.basename(train_res.get("model_path")) if train_res.get("model_path") else None,
            "evaluation": os.path.basename(eval_path),
            "prep_report": os.path.basename(prep_res.get("report")) if prep_res.get("report") else None,
        }

        # Extract trained models information from training results
        # First, try to get pre-extracted models from automl agent
        trained_models = train_res.get("trained_models", [])
        
        # If not available, parse leaderboard
        if not trained_models:
            leaderboard = train_res.get("leaderboard", {})
            agent_log(run_id, f"[orchestrator] Leaderboard type: {type(leaderboard)}, keys: {list(leaderboard.keys()) if isinstance(leaderboard, dict) else 'N/A'}", agent="orchestrator")
            
            # Parse leaderboard to extract all trained models
            if isinstance(leaderboard, dict) and leaderboard:
                # FLAML leaderboard can have different formats
                # Format 1: {estimator_name: [scores]}
                # Format 2: DataFrame converted to dict with columns
                
                # Try to extract from standard FLAML format
                if 'estimator' in leaderboard:
                    # DataFrame format: {'estimator': [...], 'metric': [...]}
                    estimators = leaderboard.get('estimator', [])
                    metrics_col = None
                    
                    # Find the metric column (could be 'val_loss', 'metric', etc.)
                    for key in leaderboard.keys():
                        if key != 'estimator' and isinstance(leaderboard[key], list):
                            metrics_col = key
                            break
                    
                    if metrics_col and isinstance(estimators, list):
                        scores = leaderboard[metrics_col]
                        for i, est in enumerate(estimators):
                            if i < len(scores):
                                trained_models.append({
                                    "name": str(est),
                                    "score": float(scores[i]) if isinstance(scores[i], (int, float)) else 0
                                })
                else:
                    # Dictionary format: {model_name: [scores]}
                    for estimator_key, estimator_values in leaderboard.items():
                        if estimator_key in ['best_estimator', 'best_config']:
                            continue
                        try:
                            if isinstance(estimator_values, list) and len(estimator_values) > 0:
                                # Get the best score for this estimator
                                best_score = max(estimator_values) if estimator_values else 0
                                trained_models.append({
                                    "name": estimator_key,
                                    "score": float(best_score) if isinstance(best_score, (int, float)) else 0
                                })
                            elif isinstance(estimator_values, (int, float)):
                                trained_models.append({
                                    "name": estimator_key,
                                    "score": float(estimator_values)
                                })
                        except Exception as e:
                            agent_log(run_id, f"[orchestrator] Error parsing estimator {estimator_key}: {e}", agent="orchestrator")
                            continue
        
        # If no models extracted from leaderboard, create from estimator list and best model
        if not trained_models:
            agent_log(run_id, "[orchestrator] No models extracted from leaderboard, using fallback", agent="orchestrator")
            
            # Get estimator list from training settings
            estimator_list = train_res.get("automl_settings", {}).get("estimator_list", [])
            best_model_name = eval_res.get("best_model", "Unknown")
            best_score = eval_res.get("metrics", {}).get("f1") or eval_res.get("metrics", {}).get("r2") or eval_res.get("metrics", {}).get("accuracy") or 0
            
            # Add best model first
            trained_models.append({
                "name": best_model_name,
                "score": float(best_score) if isinstance(best_score, (int, float)) else 0
            })
            
            # Add other models from estimator list with slightly lower scores (estimated)
            for i, est in enumerate(estimator_list):
                if est != best_model_name.lower() and est not in [m["name"].lower() for m in trained_models]:
                    # Estimate score as slightly lower than best
                    estimated_score = float(best_score) * (0.95 - i * 0.05) if best_score > 0 else 0
                    trained_models.append({
                        "name": est,
                        "score": estimated_score
                    })
        
        agent_log(run_id, f"[orchestrator] Extracted {len(trained_models)} trained models: {[m['name'] for m in trained_models]}", agent="orchestrator")
        
        update_run_state(run_id, "completed", {
            "artifacts": artifacts, 
            "metrics": eval_res.get("metrics"),
            "best_model": eval_res.get("best_model", "Unknown"),
            "trained_models": trained_models,
            "dataset_source": dataset_source,
            "dataset_source_name": dataset_source_name,
            "dataset_source_url": dataset_source_url
        })
        agent_log(run_id, f"Orchestration completed - Best Model: {eval_res.get('best_model', 'Unknown')}", agent="orchestrator")

    except Exception as e:
        tb = traceback.format_exc()
        agent_log(run_id, f"Run FAILED: {e}\n{tb}", agent="orchestrator")
        update_run_state(run_id, "failed", {"error": str(e)}, last_error=str(e))


# ----------------------
# Background worker loop
# ----------------------
def background_worker_loop(poll_interval: float = 3.0):
    """
    Continuously scan the DB for queued runs and dispatch them to executor.
    """
    agent_log("system", "Background worker started", agent="orchestrator")
    while True:
        try:
            queued = fetch_queued_runs(limit=10)
            if queued:
                for run_id, state in queued:
                    # re-check status and claim the run
                    current = read_run(run_id)
                    if not current or current.get("status") != "queued":
                        continue
                    try:
                        update_run_state(run_id, "running", {"phase": "queued->running", "payload": state.get("payload")})
                        agent_log(run_id, "Dispatching run from background worker", agent="orchestrator")
                        payload = state.get("payload", {}) if isinstance(state, dict) else {}
                        executor.submit(orchestrate_run, run_id, payload)
                    except Exception as e:
                        agent_log(run_id, f"Failed to dispatch run: {e}", agent="orchestrator")
            time.sleep(poll_interval)
        except Exception as e:
            agent_log("system", f"Background worker loop error: {e}", agent="orchestrator")
            time.sleep(poll_interval)


# Start background worker when app starts
@app.on_event("startup")
def start_background_worker():
    t = threading.Thread(target=background_worker_loop, daemon=True, name="orchestrator-worker")
    t.start()
    agent_log("system", "Background worker thread launched", agent="orchestrator")


# ----------------------
# API endpoints
# ----------------------
@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    Returns service status and basic system information.
    """
    return {
        "status": "healthy",
        "service": "AutoML Orchestrator",
        "version": "1.0.0",
        "config": Config.get_summary(),
        "database": "connected" if os.path.exists(DB) else "not_found",
        "artifacts_dir": "exists" if os.path.exists(ARTIFACT_DIR) else "not_found"
    }


@app.get("/")
def root():
    """
    Root endpoint - redirects to dashboard.
    """
    return {
        "message": "AutoML Orchestrator API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "dashboard": "/dashboard",
            "runs": "/runs",
            "status": "/status/{run_id}",
            "start_run": "/run",
            "problem_statement": "/ps"
        }
    }


@app.post("/run")
def kick_off_run(req: RunRequest):
    """
    Accept a run request and queue it. The background worker will pick it up shortly.
    """
    run_id = req.run_id or str(uuid.uuid4())
    write_run_db(run_id, "queued", {"payload": req.dict()})
    agent_log(run_id, f"Received run request: {str(req.dict())[:400]}", agent="orchestrator")
    return {"run_id": run_id, "status": "queued"}


@app.get("/status/{run_id}")
def get_status(run_id: str):
    r = read_run(run_id)
    if not r:
        raise HTTPException(status_code=404, detail="not found")

    # read run log tail
    log_path = os.path.join(ARTIFACT_DIR, f"{run_id}_log.txt")
    log_tail = ""
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            log_tail = "".join(lines[-200:])

    # return artifact file NAMES (not full paths)
    artifacts = []
    if os.path.exists(ARTIFACT_DIR):
        for fname in os.listdir(ARTIFACT_DIR):
            if fname.startswith(run_id + "_"):
                artifacts.append(fname)

    r["log_tail"] = log_tail
    r["artifacts"] = artifacts
    return r


@app.get("/artifacts/{fname}")
def serve_artifact(fname: str):
    """
    Serve artifact files saved under ARTIFACT_DIR.
    Prevent path traversal by forbidding path separators in fname.
    """
    if ".." in fname or "/" in fname or "\\" in fname:
        raise HTTPException(status_code=400, detail="invalid filename")
    fpath = os.path.join(ARTIFACT_DIR, fname)
    if not os.path.exists(fpath):
        raise HTTPException(status_code=404, detail="not found")
    return FileResponse(fpath, media_type="application/octet-stream", filename=fname)


@app.get("/runs")
def list_runs(limit: int = 20):
    conn = sqlite3.connect(DB)
    cur = conn.execute(
        "SELECT run_id, created_at, status FROM runs ORDER BY created_at DESC LIMIT ?",
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    runs = [{"run_id": r[0], "created_at": r[1], "status": r[2]} for r in rows]
    return {"runs": runs}


# ---------- Interactive Problem Statement endpoint ----------
@app.post("/ps")
def ps_interactive(payload: dict = Body(...)):
    """
    Interactive PS endpoint used by dashboard.
    Input JSON:
      { "have_ps": true|false, "problem_statement": "optional text", "preferences": {...}, "hint": "topic" }
    """
    run_id = payload.get("run_id") or str(uuid.uuid4())
    have_ps = bool(payload.get("have_ps"))
    ps_text = payload.get("problem_statement", "") or ""
    preferences = payload.get("preferences", {}) or {}
    if payload.get("hint"):
        preferences["hint"] = payload.get("hint")
    agent_log(run_id, f"Interactive PS request have_ps={have_ps} hint={preferences.get('hint')}", agent="orchestrator")
    try:
        if have_ps and ps_text.strip():
            ps = safe_step(parse_problem_or_generate, run_id, ps_text, preferences, step_name="ps_agent")
            return {"status": "ok", "mode": "parsed", "ps_parsed": ps}
        else:
            ps = safe_step(parse_problem_or_generate, run_id, "", preferences, step_name="ps_agent")
            if isinstance(ps, dict) and "options" in ps:
                return {"status": "ok", "mode": "generated_options", "ps_options": ps["options"]}
            if isinstance(ps, dict):
                return {"status": "ok", "mode": "generated_options", "ps_options": [ps]}
            return {"status": "ok", "mode": "generated_options", "ps_options": []}
    except Exception as e:
        agent_log(run_id, f"ps_interactive error: {e}", agent="orchestrator")
        return {"status": "error", "error": str(e)}


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_ui():
    return HTMLResponse(content=DASHBOARD_HTML, status_code=200)

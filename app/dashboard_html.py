# app/dashboard_html.py

DASHBOARD_HTML = r"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>AutoML Orchestrator — Dashboard</title>

  <style>
    body { font-family: Arial, Helvetica, sans-serif; margin: 18px; background: #f6f8fb; color: #0b1220 }
    .wrap { max-width: 1100px; margin: 0 auto }
    .card { background: white; border-radius: 8px; padding: 14px; margin-bottom: 12px;
            box-shadow: 0 8px 24px rgba(12,24,40,0.06) }
    textarea, input, select { width: 100%; padding: 8px; margin-top: 6px;
            border: 1px solid #e6e9ef; border-radius: 6px }
    button { padding: 8px 12px; border-radius: 6px; border: none;
            background: #0ea5a7; color: white; cursor: pointer }
    .muted { color: #6b7280; font-size: 13px }
    .log { font-family: monospace; background: #0b1220; color: #e6eef6; padding: 10px;
            border-radius: 6px; white-space: pre-wrap; max-height: 320px; overflow: auto }
    .small { font-size: 13px }
  </style>
</head>

<body>
<div class="wrap">
  <h2>AutoML Orchestrator — Interactive Dashboard</h2>

  <!-- Step 1: Dataset -->
  <div class="card">
    <h3>Step 1 — Dataset</h3>
    <div class="muted">Provide a local CSV file path or public CSV URL. Leave empty to let the Data Agent search or synthesize automatically.</div>
    <input id="upload_path" placeholder="Local path or public CSV URL (optional)"/>
  </div>

  <!-- Step 2: Topic / Hint -->
  <div class="card">
    <h3>Step 2 — Problem Topic / Hint</h3>
    <div class="muted">Provide a topic like "loan default", "diabetes detection", "customer churn", "sales forecasting", etc.</div>
    <input id="ps_hint" placeholder="e.g., loan default, churn, medical diagnosis"/>
  </div>

  <!-- Step 3 PS Block -->
  <div class="card">
    <h3>Step 3 — Problem Statement</h3>
    <div class="muted">Do you already have a written problem statement?</div>
    <button onclick="chooseHavePS(true)">Yes — I have one</button>
    <button onclick="chooseHavePS(false)" style="margin-left:6px">No — Generate options</button>

    <div id="psArea" style="margin-top:12px; display:none">
      <div id="havePSBlock">
        <label>Paste your problem statement:</label>
        <textarea id="user_ps"></textarea>
        <button onclick="callPS(true)" style="margin-top:8px">Parse & Refine PS</button>
      </div>

      <div id="noPSBlock" style="display:none">
        <div class="muted">LLM will generate 2–3 options based on your topic above.</div>
        <button onclick="callPS(false)" style="margin-top:8px">Generate Problem Statements</button>
      </div>
    </div>
  </div>

  <!-- Step 4 -->
  <div id="psResults" class="card" style="display:none">
    <h3>Generated / Parsed Problem Statements</h3>
    <div id="psOptions"></div>

    <label>Edit / Confirm Selected Problem Statement</label>
    <textarea id="selected_ps"></textarea>
    <button onclick="startRun()" style="margin-top:8px">Start AutoML Run</button>
  </div>

  <!-- Step 5 -->
  <div id="runCard" class="card" style="display:none">
    <h3>Run Status</h3>

    <label>Run ID</label>
    <input id="runid" readonly/>

    <label>Status</label>
    <div id="status" class="small muted">—</div>

    <label>Phase</label>
    <div id="phase" class="small muted">—</div>

    <label>Last Error</label>
    <div id="lasterr" class="small muted">—</div>

    <label>Logs</label>
    <div id="log" class="log">—</div>

    <label>Artifacts</label>
    <ul id="artifacts"></ul>
  </div>

</div>

<script>
let storedOptions = [];

function chooseHavePS(v){
  document.getElementById("psArea").style.display = "block";
  document.getElementById("havePSBlock").style.display = v ? "block" : "none";
  document.getElementById("noPSBlock").style.display = v ? "none" : "block";
  document.getElementById("psResults").style.display = "none";
}

async function callPS(have_ps){
  const psText = document.getElementById("user_ps").value.trim();
  const hint = document.getElementById("ps_hint").value.trim();

  if(!have_ps && !hint){
    alert("Please provide a topic/hint.");
    return;
  }

  const payload = {
    have_ps: have_ps,
    problem_statement: psText,
    hint: hint,
    preferences: {}
  };

  const res = await fetch("/ps", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  });

  const j = await res.json();
  const container = document.getElementById("psOptions");
  container.innerHTML = "";

  if(j.status !== "ok"){
    alert("Error: " + j.error);
    return;
  }

  // Parsed mode
  if(j.mode === "parsed"){
    const txt = j.ps_parsed.raw_text || JSON.stringify(j.ps_parsed, null, 2);
    container.innerHTML = `<pre>${escapeHtml(txt)}</pre>`;
    document.getElementById("selected_ps").value = txt;
  }

  // Options
  if(j.mode === "generated_options"){
    storedOptions = j.ps_options;
    let html = "<b>Generated Options</b>";
    storedOptions.forEach((opt, idx)=>{
      const txt = opt.statement || JSON.stringify(opt);
      html += `
        <div style="margin-top:10px; padding:10px; border:1px solid #ccc; border-radius:6px">
          <b>Option ${idx+1}</b>
          <pre>${escapeHtml(txt)}</pre>
          <button onclick="chooseOption(${idx})">Choose this</button>
        </div>`;
    });
    container.innerHTML = html;

    if(storedOptions.length){
      document.getElementById("selected_ps").value =
        storedOptions[0].statement || storedOptions[0].raw_text || "";
    }
  }

  document.getElementById("psResults").style.display = "block";
}

function chooseOption(idx){
  const opt = storedOptions[idx];
  document.getElementById("selected_ps").value = opt.statement;
}

async function startRun(){
  const ps = document.getElementById("selected_ps").value.trim();
  if(!ps){ alert("No problem statement selected."); return; }
  const dataset = document.getElementById("upload_path").value;

  const body = {
    user: dataset ? { upload_path: dataset } : {},
    problem_statement: ps,
    mode: "ps_provided",
    preferences: {
      allow_synthetic: true,
      training_budget_minutes: 2
    }
  };

  const res = await fetch("/run", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(body)
  });
  const j = await res.json();

  document.getElementById("runCard").style.display = "block";
  document.getElementById("runid").value = j.run_id;

  startPoll(j.run_id);
}

let poller = null;

async function startPoll(run_id){
  if(poller) clearInterval(poller);
  poller = setInterval(()=>updateStatus(run_id), 3000);
  updateStatus(run_id);
}

async function updateStatus(run_id){
  const r = await fetch("/status/" + run_id);
  if(!r.ok) return;
  const j = await r.json();

  document.getElementById("status").innerText = j.status;
  document.getElementById("phase").innerText = j.state?.phase || "-";
  document.getElementById("lasterr").innerText = j.last_error || "-";
  document.getElementById("log").innerText = j.log_tail || "-";

  const ul = document.getElementById("artifacts");
  ul.innerHTML = "";
  (j.artifacts || []).forEach(a=>{
    const li = document.createElement("li");
    li.innerHTML = `<a href="/${a}" target="_blank">${a}</a>`;
    ul.appendChild(li);
  });
}

function escapeHtml(s){
  return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}
</script>

</body>
</html>
"""

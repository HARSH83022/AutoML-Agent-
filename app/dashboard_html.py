# app/dashboard_html.py
DASHBOARD_HTML = r"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>AutoML Orchestrator — Interactive</title>
  <style>
    body{font-family:Arial,Helvetica,sans-serif;margin:18px;background:#f6f8fb;color:#0b1220}
    .wrap{max-width:1100px;margin:0 auto}
    .card{background:white;border-radius:8px;padding:14px;margin-bottom:12px;box-shadow:0 8px 24px rgba(12,24,40,0.06)}
    textarea,input,select{width:100%;padding:8px;margin-top:6px;border:1px solid #e6e9ef;border-radius:6px}
    button{padding:8px 12px;border-radius:6px;border:none;background:#0ea5a7;color:white;cursor:pointer}
    .muted{color:#6b7280;font-size:13px}
    .log{font-family:monospace;background:#0b1220;color:#e6eef6;padding:10px;border-radius:6px;white-space:pre-wrap;max-height:320px;overflow:auto}
    .small{font-size:13px}
  </style>
</head>
<body>
  <div class="wrap">
    <h2>AutoML Orchestrator — Interactive</h2>

    <!-- STEP 1 -->
    <div class="card">
      <h3>Step 1 — Do you have a dataset?</h3>
      <div class="muted">Provide local CSV path or public CSV URL. Leave empty to let the Data Agent search/synthesize.</div>
      <input id="upload_path" placeholder="Local path or public URL (optional)"/>
    </div>

    <!-- STEP 2 -->
    <div class="card">
      <h3>Step 2 — Problem Topic / Hint</h3>
      <input id="ps_hint" placeholder="e.g., diabetes detection, churn prediction"/>
    </div>

    <!-- STEP 3 -->
    <div class="card">
      <h3>Step 3 — Problem Statement</h3>
      <button onclick="chooseHavePS(true)">Yes — I have one</button>
      <button onclick="chooseHavePS(false)" style="margin-left:6px">No — Suggest options</button>

      <div id="psArea" style="display:none;margin-top:12px">
        <div id="havePSBlock">
          <textarea id="user_ps" placeholder="Paste your full problem statement"></textarea>
          <button onclick="callPS(true)" style="margin-top:8px">Parse & Refine PS</button>
        </div>

        <div id="noPSBlock" style="display:none">
          <button onclick="callPS(false)" style="margin-top:8px">Generate PS Options</button>
        </div>
      </div>
    </div>

    <!-- PS RESULTS -->
    <div id="psResults" class="card" style="display:none">
      <h3>Problem Statement — Confirm</h3>
      <div id="psOptions"></div>

      <label>Edit / Confirm Selected PS</label>
      <textarea id="selected_ps"></textarea>
      <button onclick="startRun()" style="margin-top:10px">Start Run</button>
    </div>

    <!-- RUN STATUS -->
    <div id="runCard" class="card" style="display:none">
      <h3>Run Status</h3>
      <label>Run ID</label>
      <input id="runid" readonly/>

      <label>Status</label>
      <div id="status" class="small muted">-</div>

      <label>Phase</label>
      <div id="phase" class="small muted">-</div>

      <label>Last Error</label>
      <div id="lasterr" class="small muted">-</div>

      <label>Log Tail</label>
      <div id="log" class="log">-</div>

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
  const psText = document.getElementById("user_ps").value || "";
  const hint = document.getElementById("ps_hint").value.trim();

  if(!have_ps && !hint){
    alert("Please enter a topic/hint first!");
    return;
  }

  const payload = {
    have_ps: have_ps,
    problem_statement: psText,
    hint: hint,
    preferences: {}
  };

  try{
    const res = await fetch("/ps", {
      method:"POST",
      headers:{ "Content-Type":"application/json" },
      body: JSON.stringify(payload)
    });

    const j = await res.json();
    if(j.status !== "ok"){ alert("PS Error: "+(j.error||"unknown")); return; }

    const box = document.getElementById("psOptions");
    box.innerHTML = "";

    // LLM generated OPTIONS
    if(j.mode === "generated_options"){
      storedOptions = j.ps_options;
      let html = "<b>Generated Options</b>";

      j.ps_options.forEach((opt, i)=>{
        const txt = opt.statement || opt.raw_text;
        html += `
          <div style="margin-top:8px;padding:8px;border:1px solid #ddd;border-radius:6px">
            <b>Option ${i+1}</b>
            <pre>${escapeHtml(txt)}</pre>
            <button onclick="chooseOption(${i})">Choose this</button>
          </div>`;
      });

      box.innerHTML = html;
      document.getElementById("selected_ps").value =
          j.ps_options[0].statement || j.ps_options[0].raw_text;
    }

    // USER provided PS → parsed
    if(j.mode === "parsed"){
      const txt = j.ps_parsed.raw_text;
      box.innerHTML = "<b>Parsed PS</b><pre>"+escapeHtml(txt)+"</pre>";
      document.getElementById("selected_ps").value = txt;
    }

    document.getElementById("psResults").style.display = "block";

  }catch(e){
    alert("PS request failed: "+e);
  }
}

function chooseOption(i){
  document.getElementById("selected_ps").value =
    storedOptions[i].statement || storedOptions[i].raw_text;
}

async function startRun(){
  const ps = document.getElementById("selected_ps").value.trim();
  if(!ps){ return alert("Please confirm problem statement"); }

  const upload_path = document.getElementById("upload_path").value.trim();

  const payload = {
    user: upload_path ? { upload_path: upload_path } : {},
    mode: "ps_provided",
    problem_statement: ps,
    preferences: { primary_metric:"f1", training_budget_minutes:2, allow_synthetic:true }
  };

  const res = await fetch("/run", {
    method:"POST",
    headers:{ "Content-Type":"application/json" },
    body: JSON.stringify(payload)
  });

  const j = await res.json();

  if(!j.run_id){ alert("Could not start run"); return; }

  document.getElementById("runCard").style.display = "block";
  document.getElementById("runid").value = j.run_id;

  pollStart(j.run_id);
}

let poller;
function pollStart(id){
  if(poller) clearInterval(poller);
  updateStatus(id);
  poller = setInterval(()=> updateStatus(id), 2500);
}

async function updateStatus(id){
  const res = await fetch(`/status/${id}`);
  const j = await res.json();

  document.getElementById("status").innerText = j.status;
  document.getElementById("phase").innerText = j.state?.phase || "-";
  document.getElementById("lasterr").innerText = j.last_error || "-";
  document.getElementById("log").innerText = j.log_tail || "-";

  let ul = document.getElementById("artifacts");
  ul.innerHTML = "";
  (j.artifacts || []).forEach(a=>{
    const li = document.createElement("li");
    li.innerHTML = `<a href="/artifacts/${a}" target="_blank">${a.split("/").pop()}</a>`;

    ul.appendChild(li);
  });

  if(j.status === "completed" || j.status === "failed") clearInterval(poller);
}

function escapeHtml(s){
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
</script>
</body>
</html>
"""

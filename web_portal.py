from http.server import BaseHTTPRequestHandler, HTTPServer
import json, urllib.request, subprocess, os, signal, time

def get_meta(path):
    try:
        req = urllib.request.Request(
            "http://169.254.169.254/latest/api/token",
            method="PUT",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"}
        )
        token = urllib.request.urlopen(req, timeout=1).read().decode()
        req2 = urllib.request.Request(
            f"http://169.254.169.254/latest/meta-data/{path}",
            headers={"X-aws-ec2-metadata-token": token}
        )
        return urllib.request.urlopen(req2, timeout=1).read().decode()
    except Exception:
        return "us-east-1-cloud"

def check_engine():
    try:
        res = urllib.request.urlopen("http://127.0.0.1:8080/health", timeout=0.5).read().decode()
        return True, json.loads(res)
    except Exception:
        return False, {"status": "OFFLINE", "pid": None}

def start_worker():
    subprocess.Popen(
        ["/usr/bin/python3", "/opt/self_healing_portal/order_engine.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )
    for _ in range(15):
        ok, info = check_engine()
        if ok:
            return ok, info
        time.sleep(0.05)
    return False, {"pid": None}

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Self-Healing EC2 Physical Reset | Enterprise Business Continuity</title>
<style>
:root{--bg:#f0f7ff;--card:#ffffff;--text:#0f172a;--muted:#475569;--border:#bae6fd;--accent:#0284c7;--hero:linear-gradient(125deg,#0369a1,#0284c7,#38bdf8);--table-head:#e0f2fe}
body.dark{--bg:#0b1120;--card:#111827;--text:#f1f5f9;--muted:#94a3b8;--border:#1e3a8a;--accent:#38bdf8;--hero:linear-gradient(125deg,#0f172a,#1e3a8a,#0369a1);--table-head:#1e293b}
*{box-sizing:border-box;margin:0;padding:0;font-family:'Inter','Segoe UI',system-ui,sans-serif}
body{background:var(--bg);color:var(--text);line-height:1.5;transition:background .2s,color .2s}
.alert-bar{display:none;background:#b91c1c;color:#fff;padding:16px 32px;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap}
.alert-bar.show{display:flex}
.btn-recover{background:#fff;color:#b91c1c;border:none;padding:10px 22px;border-radius:6px;font-weight:800;font-size:13px;cursor:pointer}
.ok-bar{display:none;background:#047857;color:#ecfdf5;padding:14px 32px;text-align:center;font-size:14px;font-weight:600}
.ok-bar.show{display:block}
header{background:var(--card);border-bottom:1px solid var(--border);padding:16px 36px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px}
.brand{display:flex;align-items:center;gap:10px;font-size:19px;font-weight:800;color:var(--accent)}
.badge{background:var(--accent);color:#fff;font-size:11px;padding:3px 8px;border-radius:4px;text-transform:uppercase}
.nav-right{display:flex;align-items:center;gap:12px}
.status-pill{background:#dcfce7;color:#166534;padding:6px 14px;border-radius:999px;font-size:12px;font-weight:700}
.status-pill.down{background:#fee2e2;color:#991b1b}
.btn-theme{background:var(--bg);color:var(--text);border:1px solid var(--border);padding:6px 12px;border-radius:6px;font-size:12px;font-weight:600;cursor:pointer}
.hero{background:var(--hero);color:#fff;padding:34px 36px}
.hero-inner{max-width:1140px;margin:0 auto}
.hero h1{font-size:26px;font-weight:800;margin-bottom:6px}
.hero p{font-size:14px;opacity:.92;max-width:680px}
.kpi-strip{max-width:1140px;margin:-22px auto 26px;padding:0 20px;display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.kpi{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:18px;box-shadow:0 4px 12px rgba(2,132,199,.07)}
.kpi-lbl{font-size:11px;text-transform:uppercase;color:var(--muted);font-weight:700}
.kpi-num{font-size:23px;font-weight:800;margin:4px 0}
.kpi-tag{font-size:12px;color:#059669;font-weight:600}
.container{max-width:1140px;margin:0 auto 32px;padding:0 20px;display:grid;grid-template-columns:1.5fr 1fr;gap:22px}
.section-title{font-size:15px;font-weight:800;margin-bottom:12px}
.catalog{display:grid;gap:14px}
.product{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:18px;display:flex;justify-content:space-between;align-items:center;gap:14px}
.product h3{font-size:15px;margin-bottom:4px}
.product p{font-size:13px;color:var(--muted)}
.prod-right{text-align:right;min-width:140px}
.prod-price{font-size:18px;font-weight:800;margin-bottom:6px}
.btn-add{background:var(--accent);color:#fff;border:none;padding:8px 14px;border-radius:6px;font-size:12px;font-weight:700;cursor:pointer}
.checkout-card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px;height:fit-content}
.input-grp{margin-bottom:12px}
.input-grp label{display:block;font-size:12px;font-weight:700;color:var(--muted);margin-bottom:4px}
.input-grp input{width:100%;padding:9px 12px;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:6px;font-size:13px}
.summary-row{display:flex;justify-content:space-between;padding:9px 0;border-top:1px solid var(--border);font-size:13px}
.btn-pay{width:100%;padding:12px;background:var(--accent);color:#fff;border:none;border-radius:8px;font-size:14px;font-weight:700;cursor:pointer;margin-top:8px}
.ledger{max-width:1140px;margin:0 auto 36px;padding:0 20px}
.ledger-box{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:18px 22px}
table{width:100%;border-collapse:collapse;font-size:13px;margin-top:8px}
th{text-align:left;padding:10px;background:var(--table-head);color:var(--muted);font-size:11px;text-transform:uppercase}
td{padding:10px;border-bottom:1px solid var(--border)}
.badge-paid{background:#dcfce7;color:#166534;padding:3px 8px;border-radius:4px;font-weight:700;font-size:11px}
footer{background:#0f172a;color:#cbd5e1;padding:18px 36px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px;font-size:12px}
.sim-btns{display:flex;gap:10px}
.btn-fault{background:#1e293b;color:#f8fafc;border:1px solid #38bdf8;padding:8px 14px;border-radius:6px;font-size:12px;cursor:pointer}
@media(max-width:900px){.kpi-strip,.container{grid-template-columns:1fr}}
</style>
</head>
<body>
<div id="alertBar" class="alert-bar">
  <div>&#9888; BUSINESS CONTINUITY ALERT: Payment Settlement Microservice Interrupted ($12,400/hr Revenue at Risk)</div>
  <button id="healBtn" class="btn-recover" onclick="recoverService()">&#9889; Trigger Virtual Reset Now</button>
</div>
<div id="okBar" class="ok-bar"></div>
<header>
  <div class="brand">Self-Healing EC2 Physical Reset <span class="badge">Cloud Software Edition</span></div>
  <div class="nav-right">
    <div id="statusPill" class="status-pill">&#9679; Payment Engine Active (PID: __PID__)</div>
    <button class="btn-theme" onclick="document.body.classList.toggle('dark')">Toggle Light / Dark</button>
  </div>
</header>
<section class="hero">
  <div class="hero-inner">
    <h1>Zero-Downtime Business Continuity &amp; Revenue Protection</h1>
    <p>Replacing physical desk-button hardware with autonomous software fault isolation, sub-second virtual reset recovery, and AWS EC2 Auto Scaling resilience.</p>
  </div>
</section>
<div class="kpi-strip">
  <div class="kpi"><div class="kpi-lbl">Revenue Protected</div><div class="kpi-num" id="revTotal">$48,920</div><div class="kpi-tag">Zero Lost Checkouts</div></div>
  <div class="kpi"><div class="kpi-lbl">Verified B2B Orders</div><div class="kpi-num" id="invCount">84</div><div class="kpi-tag">Port 8080 Microservice</div></div>
  <div class="kpi"><div class="kpi-lbl">Service SLA Uptime</div><div class="kpi-num" id="slaNum">99.99%</div><div class="kpi-tag" id="slaTag">AWS ASG Protected</div></div>
  <div class="kpi"><div class="kpi-lbl">Virtual Reset MTTR</div><div class="kpi-num" id="mttrNum">0.05s</div><div class="kpi-tag">No Hardware Required</div></div>
</div>
<div class="container">
  <div>
    <div class="section-title">Enterprise Cloud Continuity Solutions</div>
    <div class="catalog">
      <div class="product">
        <div><h3>Global Payment Settlement Engine</h3><p>High-availability B2B payment routing with real-time process fault isolation.</p></div>
        <div class="prod-right"><div class="prod-price">$1,200/mo</div><button class="btn-add" onclick="selectPlan('Global Payment Settlement Engine', 1200)">Select Plan</button></div>
      </div>
      <div class="product">
        <div><h3>Automated Cloud Failover Suite</h3><p>Zero-touch infrastructure self-healing backed by AWS Auto Scaling Groups.</p></div>
        <div class="prod-right"><div class="prod-price">$850/mo</div><button class="btn-add" onclick="selectPlan('Automated Cloud Failover Suite', 850)">Select Plan</button></div>
      </div>
      <div class="product">
        <div><h3>Multi-AZ Disaster Recovery Vault</h3><p>Continuous cross-availability-zone state replication with instant recovery.</p></div>
        <div class="prod-right"><div class="prod-price">$1,650/mo</div><button class="btn-add" onclick="selectPlan('Multi-AZ Disaster Recovery Vault', 1650)">Select Plan</button></div>
      </div>
    </div>
  </div>
  <div class="checkout-card">
    <div class="section-title">Live Enterprise Checkout</div>
    <div class="input-grp"><label>Corporate Client Name</label><input id="clientName" type="text" value="Apex FinTech Solutions Ltd."></div>
    <div class="input-grp"><label>Selected License</label><input id="selectedPlan" type="text" value="Global Payment Settlement Engine" readonly></div>
    <div class="summary-row"><span>Monthly License Fee</span><strong id="planPrice">$1,200.00</strong></div>
    <div class="summary-row"><span>AWS Self-Healing Protection</span><span style="color:#059669;font-weight:700">Active</span></div>
    <button class="btn-pay" onclick="processCheckout()">Authorize &amp; Settle Payment</button>
  </div>
</div>
<div class="ledger">
  <div class="ledger-box">
    <div class="section-title">Live Transaction Ledger &amp; Linux Worker Audit</div>
    <table>
      <thead><tr><th>Transaction ID</th><th>Corporate Client</th><th>Solution</th><th>Amount</th><th>Worker PID</th><th>Status</th></tr></thead>
      <tbody id="txBody">
        <tr><td><code>TXN-94A18C02</code></td><td>Vanguard Cloud Systems</td><td>Multi-AZ Disaster Recovery Vault</td><td>$1,650</td><td><code>__PID__</code></td><td><span class="badge-paid">SETTLED</span></td></tr>
      </tbody>
    </table>
  </div>
</div>
<footer>
  <div><strong>AWS Cloud Host:</strong> EC2 <code>__INST__</code> &bull; Zone <code>__AZ__</code> &bull; Auto Scaling Group <code>self-healing-asg</code></div>
  <div class="sim-btns">
    <button class="btn-fault" onclick="triggerCrash()">Simulate Microservice Crash (SIGKILL)</button>
    <button class="btn-fault" onclick="triggerAwsFailover()">Simulate Full EC2 Host Failure (ASG)</button>
  </div>
</footer>
<script>
let currentAmount = 1200, revenue = 48920, invoices = 84;
function selectPlan(name, price){currentAmount=price;document.getElementById('selectedPlan').value=name;document.getElementById('planPrice').textContent='$'+price.toLocaleString()+'.00';}
function setOutageUI(){document.getElementById('okBar').classList.remove('show');document.getElementById('alertBar').classList.add('show');const p=document.getElementById('statusPill');p.className='status-pill down';p.textContent='● Payment Engine Offline (503)';document.getElementById('slaNum').textContent='AT RISK';document.getElementById('slaTag').textContent='Trigger Virtual Reset';document.getElementById('slaTag').style.color='#dc2626';}
function processCheckout(){const client=document.getElementById('clientName').value||'Enterprise Client',plan=document.getElementById('selectedPlan').value;fetch('/api/order',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({client:client,amount:currentAmount})}).then(r=>r.json()).then(d=>{if(!d.ok){setOutageUI();alert('Checkout safely paused: Backend payment worker crashed. Click "Trigger Virtual Reset Now" in the top banner to recover.');}else{revenue+=currentAmount;invoices++;document.getElementById('revTotal').textContent='$'+revenue.toLocaleString();document.getElementById('invCount').textContent=invoices;const row=`<tr><td><code>${d.tx_id}</code></td><td>${client}</td><td>${plan}</td><td>$${currentAmount.toLocaleString()}</td><td><code>${d.pid}</code></td><td><span class="badge-paid">SETTLED</span></td></tr>`;document.getElementById('txBody').insertAdjacentHTML('afterbegin',row);}});}
function triggerCrash(){fetch('/api/crash',{method:'POST'}).then(r=>r.json()).then(()=>setOutageUI());}
function recoverService(){const btn=document.getElementById('healBtn');btn.textContent='Executing Virtual Reset...';btn.disabled=true;fetch('/api/recover',{method:'POST'}).then(r=>r.json()).then(d=>{document.getElementById('alertBar').classList.remove('show');const ob=document.getElementById('okBar');ob.textContent='✓ Virtual Reset Complete in '+d.rto+'! Fresh Payment Worker (PID '+d.pid+') is live.';ob.classList.add('show');btn.textContent='⚡ Trigger Virtual Reset Now';btn.disabled=false;const p=document.getElementById('statusPill');p.className='status-pill';p.textContent='● Payment Engine Active (PID: '+d.pid+')';document.getElementById('slaNum').textContent='99.99%';document.getElementById('slaTag').textContent='AWS ASG Protected';document.getElementById('slaTag').style.color='#059669';document.getElementById('mttrNum').textContent=d.rto;});}
function triggerAwsFailover(){if(!confirm('Terminate host EC2 instance so AWS Auto Scaling Group automatically replaces it?'))return;fetch('/api/aws-terminate',{method:'POST'}).then(r=>r.json()).then(d=>alert(d.message));}
</script></body></html>"""

class FastHTTPServer(HTTPServer):
    allow_reuse_address = True

class WebHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    def send_json(self, obj):
        data = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
    def do_GET(self):
        ok, info = check_engine()
        pid = str(info.get("pid") or "OFFLINE")
        page = HTML.replace("__INST__", get_meta("instance-id")).replace("__AZ__", get_meta("placement/availability-zone")).replace("__PID__", pid).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page)
    def do_POST(self):
        if self.path == "/api/order":
            try:
                length = int(self.headers.get("Content-Length", 0))
                raw = self.rfile.read(length)
                req = urllib.request.Request("http://127.0.0.1:8080/order", data=raw, method="POST")
                res = urllib.request.urlopen(req, timeout=0.5).read().decode()
                self.send_json(json.loads(res))
            except Exception:
                self.send_json({"ok": False})
        elif self.path == "/api/crash":
            ok, info = check_engine()
            old_pid = info.get("pid")
            if ok and old_pid:
                try:
                    os.kill(int(old_pid), signal.SIGKILL)
                except Exception:
                    pass
            subprocess.run(["pkill", "-9", "-f", "order_engine.py"], check=False)
            self.send_json({"ok": True})
        elif self.path == "/api/recover":
            t0 = time.time()
            ok, info = check_engine()
            if not ok:
                ok, info = start_worker()
            rto = f"{round(time.time() - t0, 2)}s"
            self.send_json({"ok": ok, "pid": info.get("pid"), "rto": rto})
        elif self.path == "/api/aws-terminate":
            iid = get_meta("instance-id")
            subprocess.Popen(["aws", "ec2", "terminate-instances", "--instance-ids", iid, "--region", "us-east-1"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.send_json({"message": f"EC2 {iid} terminated. AWS Auto Scaling Group is provisioning a replacement server."})

if __name__ == "__main__":
    start_worker()
    FastHTTPServer(("0.0.0.0", 80), WebHandler).serve_forever()
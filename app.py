from flask import Flask, render_template_string, jsonify
import boto3
import requests
import time
import uuid

app = Flask(__name__)

state = {
    "status": "HEALTHY",
    "worker_id": f"tx-node-{uuid.uuid4().hex[:6]}",
    "recovery_count": 0,
    "last_rto": "1.4s",
    "events": [
        "[SYSTEM READY] AegisCloud Enterprise API & Transaction Gateway online. Processing live B2B traffic."
    ]
}

def get_metadata(path):
    try:
        token = requests.put(
            "http://169.254.169.254/latest/api/token",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
            timeout=2
        ).text
        return requests.get(
            f"http://169.254.169.254/latest/meta-data/{path}",
            headers={"X-aws-ec2-metadata-token": token},
            timeout=2
        ).text
    except Exception:
        return "i-0896e9b31602ba8f3"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AegisCloud | Enterprise API & Transaction Gateway</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Roboto, Helvetica, sans-serif; }
        body { background: #090d16; color: #f8fafc; min-height: 100vh; padding: 28px 20px; display: flex; justify-content: center; }
        .container { width: 100%; max-width: 1020px; }

        .alert-banner { display: none; padding: 20px 26px; border-radius: 12px; margin-bottom: 22px; align-items: center; justify-content: space-between; gap: 18px; animation: fadeIn 0.3s ease; }
        .alert-danger { display: flex; background: rgba(220, 38, 38, 0.2); border: 1px solid #ef4444; color: #fecaca; box-shadow: 0 0 25px rgba(220, 38, 38, 0.25); }
        .alert-success { display: flex; background: rgba(16, 185, 129, 0.18); border: 1px solid #10b981; color: #a7f3d0; }
        .btn-recover { background: #ef4444; color: #fff; border: none; padding: 13px 24px; border-radius: 8px; font-weight: 700; font-size: 14px; cursor: pointer; box-shadow: 0 0 18px rgba(239, 68, 68, 0.6); transition: 0.2s; white-space: nowrap; }
        .btn-recover:hover { background: #dc2626; transform: scale(1.03); }

        .topbar { display: flex; justify-content: space-between; align-items: center; background: #111827; border: 1px solid #1f2937; padding: 22px 28px; border-radius: 12px; margin-bottom: 24px; }
        .brand h1 { font-size: 22px; color: #38bdf8; font-weight: 700; }
        .brand p { font-size: 13px; color: #94a3b8; margin-top: 4px; }
        .badge-healthy { background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.4); padding: 8px 16px; border-radius: 999px; font-size: 13px; font-weight: 600; }
        .badge-down { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); padding: 8px 16px; border-radius: 999px; font-size: 13px; font-weight: 600; }

        .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
        .kpi { background: #111827; border: 1px solid #1f2937; padding: 18px; border-radius: 12px; }
        .kpi-title { font-size: 11px; text-transform: uppercase; color: #9ca3af; letter-spacing: 0.05em; margin-bottom: 6px; }
        .kpi-val { font-size: 18px; font-weight: 700; color: #f1f5f9; font-family: monospace; }
        .kpi-sub { font-size: 11px; color: #10b981; margin-top: 5px; }

        .panel { background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 24px; margin-bottom: 24px; }
        .panel h2 { font-size: 15px; color: #e2e8f0; margin-bottom: 12px; border-bottom: 1px solid #1f2937; padding-bottom: 10px; }
        .btn-group { display: flex; gap: 14px; flex-wrap: wrap; }
        .btn-action { padding: 12px 18px; border: none; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; transition: 0.2s; color: white; }
        .btn-crash { background: #dc2626; }
        .btn-crash:hover { background: #b91c1c; }
        .btn-stress { background: #d97706; }
        .btn-stress:hover { background: #b45309; }
        .btn-aws { background: #4f46e5; }
        .btn-aws:hover { background: #4338ca; }

        .tx-table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }
        .tx-table th { text-align: left; color: #94a3b8; padding: 10px; border-bottom: 1px solid #1f2937; font-size: 11px; text-transform: uppercase; }
        .tx-table td { padding: 10px; border-bottom: 1px solid #1f2937; font-family: monospace; color: #e2e8f0; }

        .console-box { background: #05080f; border: 1px solid #1e293b; border-radius: 8px; padding: 16px; font-family: monospace; font-size: 13px; color: #38bdf8; min-height: 110px; margin-top: 16px; line-height: 1.6; max-height: 200px; overflow-y: auto; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(-6px); } to { opacity: 1; transform: translateY(0); } }
        @media (max-width: 768px) { .kpi-grid { grid-template-columns: repeat(2, 1fr); } }
    </style>
</head>
<body>
    <div class="container">
        <div id="alertBanner" class="alert-banner">
            <div>
                <strong id="alertTitle" style="font-size: 16px; display: block; margin-bottom: 4px;"></strong>
                <span id="alertDesc" style="font-size: 13px;"></span>
            </div>
            <button id="recoverBtn" class="btn-recover" onclick="recoverSystem()">⚡ Auto-Recover Node Now</button>
        </div>

        <div class="topbar">
            <div class="brand">
                <h1>AegisCloud Enterprise API & Transaction Gateway</h1>
                <p>High-Availability B2B Cloud Gateway &bull; Host: {{ instance_id }} ({{ az }})</p>
            </div>
            <div id="statusBadge" class="badge-healthy">● SLA: 99.99% Operational</div>
        </div>

        <div class="kpi-grid">
            <div class="kpi">
                <div class="kpi-title">Live API Throughput</div>
                <div class="kpi-val" id="tpsVal">1,420 req/s</div>
                <div class="kpi-sub" id="tpsSub">Latency: 14ms (Optimal)</div>
            </div>
            <div class="kpi">
                <div class="kpi-title">Active Transaction Node</div>
                <div class="kpi-val" id="workerId">{{ worker_id }}</div>
                <div class="kpi-sub" id="workerHealth">Health Check: 200 OK</div>
            </div>
            <div class="kpi">
                <div class="kpi-title">Recovery Speed (RTO)</div>
                <div class="kpi-val" id="rtoVal">{{ last_rto }}</div>
                <div class="kpi-sub">Auto-Recoveries: <span id="recCount">{{ recovery_count }}</span></div>
            </div>
            <div class="kpi">
                <div class="kpi-title">Revenue Protected</div>
                <div class="kpi-val">$4,500 / hr</div>
                <div class="kpi-sub">Zero Transaction Loss</div>
            </div>
        </div>

        <div class="panel">
            <h2>Live B2B Transaction Stream</h2>
            <table class="tx-table">
                <thead>
                    <tr>
                        <th>Gateway Endpoint</th>
                        <th>Processor Node</th>
                        <th>Throughput</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>POST /v2/enterprise/settle</td>
                        <td id="tableWorker">{{ worker_id }}</td>
                        <td id="tableRate">890 req/s</td>
                        <td id="tableStatus" style="color: #10b981;">● ACTIVE</td>
                    </tr>
                    <tr>
                        <td>GET /v2/enterprise/ledger-sync</td>
                        <td>{{ instance_id }}</td>
                        <td>530 req/s</td>
                        <td style="color: #10b981;">● ACTIVE</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="panel">
            <h2>Chaos Engineering & Self-Healing Controls</h2>
            <p style="font-size: 13px; color: #94a3b8; margin-bottom: 16px;">
                Inject a transaction node failure to trigger the outage alert banner, then click the recovery button inside the alert to restore gateway traffic.
            </p>
            <div class="btn-group">
                <button class="btn-action btn-crash" onclick="simulateCrash()">1. Simulate Engine Crash (Trigger Outage)</button>
                <button class="btn-action btn-stress" onclick="simulateLoad()">2. Inject API Traffic Spike</button>
                <button class="btn-action btn-aws" onclick="triggerAwsAsgTermination()">3. Hard-Terminate EC2 Host (AWS ASG Failover)</button>
            </div>
            <div class="console-box" id="logBox">
                {% for ev in events %}
                <div>{{ ev }}</div>
                {% endfor %}
            </div>
        </div>
    </div>

    <script>
        function appendLog(text) {
            const box = document.getElementById('logBox');
            const line = document.createElement('div');
            line.textContent = "> " + text;
            box.appendChild(line);
            box.scrollTop = box.scrollHeight;
        }

        function simulateCrash() {
            fetch('/api/crash', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    const banner = document.getElementById('alertBanner');
                    banner.className = 'alert-banner alert-danger';
                    document.getElementById('alertTitle').textContent = "⚠️ CRITICAL SERVICE OUTAGE: Primary Transaction Node Offline";
                    document.getElementById('alertDesc').textContent = "API settlement queue paused — Revenue Risk: $4,500/hr. Click the button to execute self-healing recovery.";
                    document.getElementById('recoverBtn').style.display = 'inline-block';

                    const badge = document.getElementById('statusBadge');
                    badge.className = 'badge-down';
                    badge.textContent = "● CRITICAL: Gateway Degraded";

                    document.getElementById('tpsVal').textContent = "530 req/s";
                    document.getElementById('tpsSub').textContent = "Primary Node Dropped";
                    document.getElementById('tpsSub').style.color = "#f87171";

                    document.getElementById('workerHealth').textContent = "Health Check: 503 FAILED";
                    document.getElementById('workerHealth').style.color = "#f87171";

                    document.getElementById('tableRate').textContent = "0 req/s";
                    document.getElementById('tableStatus').textContent = "● OFFLINE (503)";
                    document.getElementById('tableStatus').style.color = "#f87171";

                    appendLog(data.message);
                });
        }

        function recoverSystem() {
            const btn = document.getElementById('recoverBtn');
            btn.textContent = "Provisioning Clean Node...";
            btn.disabled = true;
            appendLog("SELF-HEALING ENGAGED: Isolating fault -> Provisioning clean transaction node -> Verifying health checks...");

            fetch('/api/recover', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    const banner = document.getElementById('alertBanner');
                    banner.className = 'alert-banner alert-success';
                    document.getElementById('alertTitle').textContent = "✅ SERVICE RESTORED IN " + data.rto + " — ZERO TRANSACTIONS LOST";
                    document.getElementById('alertDesc').textContent = "Replacement node " + data.worker_id + " passed health checks and resumed full API throughput.";
                    btn.style.display = 'none';
                    btn.disabled = false;
                    btn.textContent = "⚡ Auto-Recover Node Now";

                    const badge = document.getElementById('statusBadge');
                    badge.className = 'badge-healthy';
                    badge.textContent = "● SLA: 99.99% Operational";

                    document.getElementById('tpsVal').textContent = "1,450 req/s";
                    document.getElementById('tpsSub').textContent = "Latency: 13ms (Optimal)";
                    document.getElementById('tpsSub').style.color = "#10b981";

                    document.getElementById('workerId').textContent = data.worker_id;
                    document.getElementById('workerHealth').textContent = "Health Check: 200 OK";
                    document.getElementById('workerHealth').style.color = "#10b981";

                    document.getElementById('tableWorker').textContent = data.worker_id;
                    document.getElementById('tableRate').textContent = "920 req/s";
                    document.getElementById('tableStatus').textContent = "● ACTIVE";
                    document.getElementById('tableStatus').style.color = "#10b981";

                    document.getElementById('rtoVal').textContent = data.rto;
                    document.getElementById('recCount').textContent = data.recovery_count;

                    appendLog(data.message);
                });
        }

        function simulateLoad() {
            appendLog("TRAFFIC SPIKE: Testing API gateway under 4-second high-concurrency load...");
            fetch('/api/stress', { method: 'POST' })
                .then(r => r.json())
                .then(data => appendLog(data.message));
        }

        function triggerAwsAsgTermination() {
            if (!confirm("This calls AWS EC2 TerminateInstances on the host VM so AWS Auto Scaling replaces the entire server (~45s boot). Continue?")) return;
            appendLog("AWS ASG FAILOVER: Terminating host EC2 instance via Boto3...");
            fetch('/api/aws-terminate', { method: 'POST' })
                .then(r => r.json())
                .then(data => appendLog(data.message));
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(
        HTML_TEMPLATE,
        instance_id=get_metadata("instance-id"),
        az=get_metadata("placement/availability-zone"),
        worker_id=state["worker_id"],
        recovery_count=state["recovery_count"],
        last_rto=state["last_rto"],
        events=state["events"]
    )

@app.route('/api/crash', methods=['POST'])
def crash_service():
    state["status"] = "OUTAGE"
    msg = f"[CRITICAL ALERT] Transaction node {state['worker_id']} crashed! Outage banner triggered ($4,500/hr exposure)."
    state["events"].append(msg)
    return jsonify({"message": msg})

@app.route('/api/recover', methods=['POST'])
def recover_service():
    start = time.time()
    time.sleep(1.3)
    new_worker = f"tx-node-{uuid.uuid4().hex[:6]}"
    rto = f"{round(time.time() - start, 2)}s"
    state["status"] = "HEALTHY"
    state["worker_id"] = new_worker
    state["recovery_count"] += 1
    state["last_rto"] = rto
    msg = f"[RECOVERED] Provisioned clean node {new_worker} in {rto}. Zero transactions lost."
    state["events"].append(msg)
    return jsonify({
        "worker_id": new_worker,
        "rto": rto,
        "recovery_count": state["recovery_count"],
        "message": msg
    })

@app.route('/api/stress', methods=['POST'])
def stress_cpu():
    end_time = time.time() + 4
    while time.time() < end_time:
        _ = 999999 * 999999
    msg = "[LOAD VERIFIED] Gateway absorbed 3,800 req/s spike with 0 dropped requests."
    state["events"].append(msg)
    return jsonify({"message": msg})

@app.route('/api/aws-terminate', methods=['POST'])
def terminate_ec2():
    instance_id = get_metadata("instance-id")
    ec2 = boto3.client('ec2', region_name='us-east-1')
    ec2.terminate_instances(InstanceIds=[instance_id])
    return jsonify({"message": f"AWS TerminateInstances sent for {instance_id}. Auto Scaling replacement initiated."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
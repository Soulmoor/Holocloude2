"""
Holocloude Dashboard Module
==========================
Ausgelagert aus pi_control_v8_AI-extendet.py für bessere Code-Organisation.

Enthält:
- DASHBOARD_HTML: Das vollständige HTML-Template für die Web-Oberfläche
- DashboardCache: Caching-System für das generierte HTML
"""

import hashlib
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# ULTIMATE PROFESSIONAL DASHBOARD
# =============================================================================
# HINWEIS: Dies ist der vollständige HTML-Code, der für die Web-Oberfläche benötigt wird.
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pi-Control Ultimate v8.0</title>
    <style>
        :root {
            --bg: #0a0a0a;
            --bg-secondary: #121212;
            --card: #1a1a1a;
            --card-hover: #222;
            --text: #e0e0e0;
            --text-dim: #888;
            --accent: #00d4ff;
            --success: #00ff88;
            --warning: #ffaa00;
            --danger: #ff4444;
            --border: #333;
            --shadow: rgba(0, 0, 0, 0.5);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            overflow-x: hidden;
        }

        .container {
            max-width: 1800px;
            margin: 0 auto;
            padding: 20px;
        }

        /* Header */
        header {
            background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px var(--shadow);
            border: 1px solid var(--border);
        }

        h1 {
            font-size: 2.8em;
            background: linear-gradient(135deg, var(--accent), var(--success));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            text-align: center;
        }

        .subtitle {
            text-align: center;
            color: var(--text-dim);
            font-size: 1.1em;
        }

        .header-stats {
            display: flex;
            justify-content: space-around;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
        }

        .header-stat {
            text-align: center;
        }

        .header-stat-value {
            font-size: 2em;
            font-weight: bold;
            color: var(--accent);
        }

        .header-stat-label {
            font-size: 0.9em;
            color: var(--text-dim);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* Tabs */
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 25px;
            border-bottom: 2px solid var(--border);
            flex-wrap: wrap;
        }

        .tab {
            padding: 15px 30px;
            background: transparent;
            border: none;
            color: var(--text-dim);
            cursor: pointer;
            transition: all 0.3s;
            border-bottom: 3px solid transparent;
            font-size: 1.05em;
            font-weight: 500;
        }

        .tab:hover {
            color: var(--text);
            background: rgba(255, 255, 255, 0.05);
        }

        .tab.active {
            color: var(--accent);
            border-bottom-color: var(--accent);
        }

        .tab-content {
            display: none;
            animation: fadeIn 0.3s;
        }

        .tab-content.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Grid System */
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .grid-2 {
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
        }

        .grid-full {
            grid-template-columns: 1fr;
        }

        /* Cards */
        .card {
            background: var(--card);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid var(--border);
            box-shadow: 0 5px 20px var(--shadow);
            transition: all 0.3s;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px var(--shadow);
        }

        .card h2 {
            font-size: 1.4em;
            margin-bottom: 20px;
            color: var(--accent);
            display: flex;
            align-items: center;
            gap: 10px;
            padding-bottom: 15px;
            border-bottom: 2px solid var(--border);
        }

        /* NAS Status Display */
        .status-display {
            text-align: center;
            padding: 30px;
            border-radius: 12px;
            font-size: 2.2em;
            font-weight: bold;
            margin: 20px 0;
            text-transform: uppercase;
            letter-spacing: 3px;
            position: relative;
            overflow: hidden;
        }

        .status-display::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: pulse 3s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 0.5; }
            50% { transform: scale(1.1); opacity: 0.8; }
        }

        .status-online {
            background: linear-gradient(135deg, #00ff88, #00cc66);
            color: #000;
            box-shadow: 0 0 30px rgba(0, 255, 136, 0.5);
        }

        .status-offline {
            background: linear-gradient(135deg, #ff4444, #cc0000);
            color: #fff;
            box-shadow: 0 0 30px rgba(255, 68, 68, 0.5);
        }

        .status-busy {
            background: linear-gradient(135deg, #ffaa00, #ff8800);
            color: #000;
            box-shadow: 0 0 30px rgba(255, 170, 0, 0.5);
            animation: busyPulse 1s ease-in-out infinite;
        }

        @keyframes busyPulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.02); }
        }

        .status-idle {
            background: linear-gradient(135deg, #00d4ff, #0099cc);
            color: #000;
            box-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
        }

        /* Log Console */
        .log-console {
            background: #000;
            border: 1px solid #333;
            border-radius: 10px;
            padding: 15px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            height: 500px;
            overflow-y: auto;
        }
        .log-entry {
            margin-bottom: 5px;
            border-bottom: 1px solid #111;
            padding-bottom: 2px;
        }
        .log-time { color: #666; margin-right: 10px; }
        .log-INFO { color: #e0e0e0; }
        .log-WARNING { color: var(--warning); }
        .log-ERROR { color: var(--danger); font-weight: bold; }

        /* Stats Grid */
        .stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-top: 15px;
        }

        .stat {
            background: rgba(255, 255, 255, 0.03);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid var(--border);
            transition: all 0.3s;
        }

        .stat:hover {
            background: rgba(255, 255, 255, 0.06);
            border-color: var(--accent);
        }

        .stat-label {
            font-size: 0.85em;
            color: var(--text-dim);
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .stat-value {
            font-size: 1.8em;
            font-weight: bold;
            color: var(--text);
        }

        .stat-value.good { color: var(--success); }
        .stat-value.warn { color: var(--warning); }
        .stat-value.crit { color: var(--danger); }

        /* Buttons */
        .buttons {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 12px;
            margin-top: 20px;
        }

        .btn {
            padding: 16px 20px;
            border: none;
            border-radius: 10px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }

        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
        }

        .btn:active {
            transform: translateY(0);
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--accent), #0099cc);
            color: #000;
        }

        .btn-success {
            background: linear-gradient(135deg, var(--success), #00cc66);
            color: #000;
        }

        .btn-warning {
            background: linear-gradient(135deg, var(--warning), #ff8800);
            color: #000;
        }

        .btn-danger {
            background: linear-gradient(135deg, var(--danger), #cc0000);
            color: #fff;
        }

        /* Badges */
        .badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
        }

        .badge-success { background: var(--success); color: #000; }
        .badge-warning { background: var(--warning); color: #000; }
        .badge-danger { background: var(--danger); color: #fff; }
        .badge-info { background: var(--accent); color: #000; }

        /* Connection List */
        .connection-list {
            max-height: 400px;
            overflow-y: auto;
            padding-right: 10px;
        }

        .connection-item {
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            margin-bottom: 12px;
            border-radius: 10px;
            border-left: 4px solid var(--accent);
            transition: all 0.3s;
        }

        .connection-item:hover {
            background: rgba(255, 255, 255, 0.08);
            transform: translateX(5px);
        }

        .connection-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .connection-ip {
            font-family: 'Courier New', monospace;
            color: var(--accent);
            font-weight: bold;
            font-size: 1.1em;
        }

        .connection-details {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            font-size: 0.9em;
            color: var(--text-dim);
        }

        .connection-detail {
            display: flex;
            flex-direction: column;
        }

        .connection-detail-label {
            font-size: 0.8em;
            color: var(--text-dim);
        }

        .connection-detail-value {
            color: var(--text);
            font-weight: bold;
        }

        /* Skills Management */
        .skill-item {
            background: rgba(255, 255, 255, 0.03);
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid var(--border);
            transition: all 0.3s;
        }

        .skill-item:hover {
            background: rgba(255, 255, 255, 0.06);
            border-color: var(--accent);
        }

        .skill-name {
            font-size: 1.1em;
            font-weight: 500;
        }

        .skill-toggle {
            position: relative;
            width: 60px;
            height: 30px;
            cursor: pointer;
        }

        .skill-toggle input {
            display: none;
        }

        .skill-toggle-slider {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: #333;
            border-radius: 30px;
            transition: 0.3s;
        }

        .skill-toggle-slider:before {
            position: absolute;
            content: "";
            height: 22px;
            width: 22px;
            left: 4px;
            bottom: 4px;
            background: white;
            border-radius: 50%;
            transition: 0.3s;
        }

        .skill-toggle input:checked + .skill-toggle-slider {
            background: var(--success);
        }

        .skill-toggle input:checked + .skill-toggle-slider:before {
            transform: translateX(30px);
        }

        /* Progress Bar */
        .progress-bar {
            height: 12px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            overflow: hidden;
            margin: 10px 0;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--accent), var(--success));
            transition: width 0.5s;
            position: relative;
            overflow: hidden;
        }

        .progress-fill::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            animation: shimmer 2s infinite;
        }

        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }

        /* Gauge */
        .gauge {
            position: relative;
            width: 150px;
            height: 150px;
            margin: 20px auto;
        }

        .gauge-circle {
            transform: rotate(-90deg);
        }

        .gauge-value {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 2em;
            font-weight: bold;
        }

        /* Empty State */
        .empty-state {
            text-align: center;
            padding: 50px;
            color: var(--text-dim);
            font-size: 1.1em;
        }

        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
        }

        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 5px;
        }

        ::-webkit-scrollbar-thumb {
            background: var(--accent);
            border-radius: 5px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: var(--success);
        }

        /* Toast Notifications */
        .toast {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: var(--card);
            border: 1px solid var(--accent);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 10px 40px var(--shadow);
            z-index: 1000;
            animation: slideIn 0.3s;
        }

        @keyframes slideIn {
            from { transform: translateX(400px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }

        /* Presence-specific styles */
        .presence-mode-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 20px;
            border-radius: 25px;
            font-size: 1.1em;
            font-weight: bold;
            margin: 10px 0;
        }

        .presence-mode-badge.work_day {
            background: linear-gradient(135deg, #4a90d9, #357abd);
            color: #fff;
        }

        .presence-mode-badge.free_day {
            background: linear-gradient(135deg, #ff6b9d, #c44569);
            color: #fff;
        }

        .presence-mode-badge.weekend {
            background: linear-gradient(135deg, #a29bfe, #6c5ce7);
            color: #fff;
        }

        .presence-mode-badge.home_office {
            background: linear-gradient(135deg, #fdcb6e, #f39c12);
            color: #000;
        }

        .presence-mode-badge.unknown {
            background: linear-gradient(135deg, #636e72, #2d3436);
            color: #fff;
        }

        .prediction-card {
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 255, 136, 0.1));
            border: 1px solid var(--accent);
            border-radius: 15px;
            padding: 20px;
            margin-top: 15px;
        }

        .prediction-time {
            font-size: 2.5em;
            font-weight: bold;
            color: var(--accent);
            text-align: center;
        }

        .prediction-window {
            text-align: center;
            color: var(--text-dim);
            font-size: 0.95em;
            margin-top: 5px;
        }

        .confidence-bar {
            height: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 15px;
        }

        .confidence-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.5s, background 0.5s;
        }

        .confidence-fill.high {
            background: linear-gradient(90deg, var(--success), #00cc66);
        }

        .confidence-fill.medium {
            background: linear-gradient(90deg, var(--warning), #ff8800);
        }

        .confidence-fill.low {
            background: linear-gradient(90deg, var(--danger), #cc0000);
        }

        /* Responsive */
        @media (max-width: 768px) {
            .grid, .grid-2 {
                grid-template-columns: 1fr;
            }

            h1 {
                font-size: 2em;
            }

            .connection-details {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Pi-Control Ultimate</h1>
            <div class="subtitle">Goal-Oriented Intelligent Agent - v8.0</div>
            <div class="header-stats">
                <div class="header-stat">
                    <div class="header-stat-value" id="total-utility">0%</div>
                    <div class="header-stat-label">Total Utility</div>
                </div>
                <div class="header-stat">
                    <div class="header-stat-value" id="observations-count">0</div>
                    <div class="header-stat-label">Observations</div>
                </div>
                <div class="header-stat">
                    <div class="header-stat-value" id="active-tests">0</div>
                    <div class="header-stat-label">A/B Tests</div>
                </div>
            </div>
        </header>

        <div class="tabs">
            <button class="tab active" onclick="showTab('overview')">Uebersicht</button>
            <button class="tab" onclick="showTab('nas')">NAS Control</button>
            <button class="tab" onclick="showTab('events')">NAS Events</button>
            <button class="tab" onclick="showTab('presence')">Presence</button>
            <button class="tab" onclick="showTab('connections')">Verbindungen</button>
            <button class="tab" onclick="showTab('system')">System</button>
            <button class="tab" onclick="showTab('ai-learning')">AI Learning</button>
            <button class="tab" onclick="showTab('goals')">Goals</button>
            <button class="tab" onclick="showTab('skills')">Skills</button>
            <button class="tab" onclick="showTab('learning')">Learning</button>
            <button class="tab" onclick="showTab('logs')">Logs</button>
            <button class="tab" onclick="showTab('errors')">Errors</button>
            <button class="tab" onclick="showTab('ram')">RAM</button>
            <!-- SKILL_TABS_PLACEHOLDER -->
            </div>

        <div id="tab-overview" class="tab-content active">
            <div class="grid">
                <div class="card">
                    <h2>NAS Status</h2>
                    <div id="nas-status-quick" class="status-display status-offline">OFFLINE</div>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-label">State</div>
                            <div class="stat-value" id="nas-state-quick">Unknown</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Load</div>
                            <div class="stat-value" id="nas-load-quick">0%</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Connections</div>
                            <div class="stat-value good" id="nas-conn-quick">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Idle</div>
                            <div class="stat-value" id="nas-idle-quick">0m</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>System Health</h2>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-label">CPU Temp</div>
                            <div class="stat-value" id="cpu-temp-quick">--C</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">CPU Usage</div>
                            <div class="stat-value" id="cpu-usage-quick">--%</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">RAM Usage</div>
                            <div class="stat-value" id="ram-usage-quick">--%</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Governor</div>
                            <div class="stat-value" style="font-size:1em" id="governor-quick">...</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>Quick Actions</h2>
                    <div class="buttons">
                        <button class="btn btn-success" onclick="sendAction('wake')">
                            Wake NAS
                        </button>
                        <button class="btn btn-warning" onclick="sendAction('suspend')">
                            Suspend Request
                        </button>
                        <button class="btn btn-danger" onclick="sendAction('force_suspend')">
                            Force Suspend
                        </button>
                    </div>
                </div>

                <div class="card">
                    <h2>Decision Engine</h2>
                    <div class="stat">
                        <div class="stat-label">Last Decision</div>
                        <div class="stat-value" style="font-size:1.1em" id="last-decision">--</div>
                    </div>
                    <div class="stat" style="margin-top:15px">
                        <div class="stat-label">Current Plan</div>
                        <div class="stat-value" style="font-size:0.9em" id="current-plan">No active plan</div>
                    </div>
                </div>
            </div>
        </div>


        <div id="tab-ai-learning" class="tab-content">
            <div class="grid">
                <div class="card">
                    <h2>AI Learning System</h2>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-label">Bayesian Contexts</div>
                            <div class="stat-value" id="ai-bayesian-contexts">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Q-Learning Updates</div>
                            <div class="stat-value" id="ai-ql-updates">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Total AI Observations</div>
                            <div class="stat-value" id="ai-total-obs">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Avg Q-Value</div>
                            <div class="stat-value" id="ai-avg-q">0.0</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>AI Prediction</h2>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-label">NAS Usage Probability</div>
                            <div class="stat-value" id="ai-nas-prob">-</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Recommended Action</div>
                            <div class="stat-value" id="ai-recommended">-</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Confidence</div>
                            <div class="stat-value" id="ai-confidence">-</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div id="tab-nas" class="tab-content">
            <div class="grid grid-2">
                <div class="card">
                    <h2>NAS Status & Control</h2>
                    <div id="nas-status-full" class="status-display status-offline">OFFLINE</div>

                    <div class="stats">
                        <div class="stat">
                            <div class="stat-label">IP Address</div>
                            <div class="stat-value" style="font-size:1.1em" id="nas-ip">...</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">State</div>
                            <div class="stat-value" id="nas-state">...</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Load</div>
                            <div class="stat-value" id="nas-load">0%</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Active Connections</div>
                            <div class="stat-value good" id="nas-connections">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">CPU Usage</div>
                            <div class="stat-value" id="nas-cpu">0%</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">RAM Usage</div>
                            <div class="stat-value" id="nas-ram">0%</div>
                        </div>
                    </div>

                    <h3 style="margin-top:25px; margin-bottom:15px; color:var(--accent)">Control Actions</h3>
                    <div class="buttons">
                        <button class="btn btn-success" onclick="sendAction('wake')">
                            Wake on LAN
                        </button>
                        <button class="btn btn-warning" onclick="sendAction('suspend')">
                            Suspend Request (UDP)
                        </button>
                        <button class="btn btn-danger" onclick="sendAction('force_suspend')">
                            Force Suspend (SSH)
                        </button>
                    </div>
                </div>

                <div class="card">
                    <h2>NAS Statistics</h2>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-label">Total WoL Sent</div>
                            <div class="stat-value" id="total-wol">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Total Shutdowns</div>
                            <div class="stat-value" id="total-shutdowns">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Idle Time</div>
                            <div class="stat-value" id="idle-time">0m</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Last Activity</div>
                            <div class="stat-value" style="font-size:1em" id="last-activity">--</div>
                        </div>
                    </div>

                    <h3 style="margin-top:25px; margin-bottom:15px; color:var(--accent)">Probability Analysis</h3>
                    <div>
                        <div class="stat-label">NAS Needed Probability</div>
                        <div class="progress-bar">
                            <div id="nas-prob-bar" class="progress-fill" style="width:0%"></div>
                        </div>
                        <div style="text-align:right; color:var(--text-dim); margin-top:5px" id="nas-prob-pct">0%</div>
                    </div>
                </div>
            </div>
        </div>

        <div id="tab-events" class="tab-content">
            <div class="grid grid-2">
                <div class="card">
                    <h2>NAS Event History</h2>
                    <p style="color:var(--text-dim); margin-bottom:15px">Alle Wake/Sleep-Aktionen mit Zeitstempel und Ausloeser</p>
                    <div id="nas-events-list" class="log-console" style="height:400px">
                        <div class="empty-state">Keine Events aufgezeichnet</div>
                    </div>
                </div>

                <div class="card">
                    <h2>Manual Override Status</h2>
                    <div id="override-status" class="status-display status-offline" style="font-size:1.5em">
                        INAKTIV
                    </div>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-label">Override Action</div>
                            <div class="stat-value" id="override-action">-</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Verbleibend</div>
                            <div class="stat-value" id="override-remaining">-</div>
                        </div>
                    </div>
                    <p style="color:var(--text-dim); margin-top:15px; font-size:0.9em">
                        Manual Override wird aktiv, wenn du Wake/Suspend manuell ausloest.
                        Die KI trifft dann fuer 10-15 Minuten keine NAS-Entscheidungen.
                    </p>
                    <button class="btn btn-warning" style="margin-top:15px" onclick="sendAction('clear_override')">
                        Override aufheben
                    </button>
                </div>
            </div>

            <div class="grid grid-full" style="margin-top:20px">
                <div class="card">
                    <h2>Event Statistik</h2>
                    <div class="stats" style="grid-template-columns: repeat(5, 1fr)">
                        <div class="stat">
                            <div class="stat-label">AI Wakes</div>
                            <div class="stat-value good" id="stat-ai-wakes">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Proxy Wakes</div>
                            <div class="stat-value" id="stat-proxy-wakes">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Manual Wakes</div>
                            <div class="stat-value" id="stat-manual-wakes">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Idle Sleeps</div>
                            <div class="stat-value" id="stat-idle-sleeps">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Away Sleeps</div>
                            <div class="stat-value warning" id="stat-away-sleeps">0</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- PRESENCE TAB -->
        <div id="tab-presence" class="tab-content">
            <div class="grid">
                <div class="card">
                    <h2>Presence Status</h2>
                    <div id="presence-status" class="status-display status-online">ZUHAUSE</div>

                    <div style="text-align:center; margin: 15px 0;">
                        <div id="presence-mode-badge" class="presence-mode-badge unknown">
                            <span id="presence-mode-icon">?</span>
                            <span id="presence-mode-text">Unbekannt</span>
                        </div>
                    </div>

                    <div class="stats">
                        <div class="stat">
                            <div class="stat-label">Tages-Modus</div>
                            <div class="stat-value" style="font-size:1.2em" id="presence-day-mode">Unbekannt</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Erkannt um</div>
                            <div class="stat-value" id="presence-mode-time">--:--</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Grund</div>
                            <div class="stat-value" style="font-size:0.9em" id="presence-mode-reason">--</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">User Status</div>
                            <div class="stat-value" id="presence-user-status">Zuhause</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>Aktuelle Vorhersage</h2>
                    <div id="presence-prediction-container">
                        <div class="prediction-card">
                            <div class="stat-label" style="text-align:center">Erwartete Rueckkehr</div>
                            <div class="prediction-time" id="presence-return-time">--:--</div>
                            <div class="prediction-window" id="presence-window">Zeitfenster: -- bis --</div>

                            <div style="margin-top:20px">
                                <div style="display:flex; justify-content:space-between; margin-bottom:5px">
                                    <span class="stat-label">Konfidenz</span>
                                    <span id="presence-confidence-pct">--%</span>
                                </div>
                                <div class="confidence-bar">
                                    <div id="presence-confidence-bar" class="confidence-fill medium" style="width:0%"></div>
                                </div>
                            </div>
                        </div>

                        <div class="stats" style="margin-top:15px">
                            <div class="stat">
                                <div class="stat-label">Kategorie</div>
                                <div class="stat-value" style="font-size:1.2em" id="presence-category">--</div>
                            </div>
                            <div class="stat">
                                <div class="stat-label">Basierend auf</div>
                                <div class="stat-value" style="font-size:1em" id="presence-sample-size">-- Events</div>
                            </div>
                        </div>
                    </div>

                    <div id="presence-no-prediction" style="display:none">
                        <div class="empty-state">
                            <div style="font-size:3em; margin-bottom:15px">Home</div>
                            <div>User ist zuhause</div>
                            <div style="font-size:0.9em; margin-top:10px; color:var(--text-dim)">
                                Vorhersage wird angezeigt wenn User das Haus verlaesst
                            </div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>Lern-Statistiken</h2>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-label">Arbeitstage erfasst</div>
                            <div class="stat-value good" id="presence-work-count">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Durchschn. Arbeitszeit</div>
                            <div class="stat-value" id="presence-work-avg">--h</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Short Trips erfasst</div>
                            <div class="stat-value" id="presence-short-count">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Durchschn. Trip-Dauer</div>
                            <div class="stat-value" id="presence-short-avg">--min</div>
                        </div>
                    </div>

                    <div style="margin-top:20px; padding-top:15px; border-top:1px solid var(--border)">
                        <div class="stat-label">Gesamt gelernte Events</div>
                        <div class="progress-bar" style="margin-top:10px">
                            <div id="presence-learning-bar" class="progress-fill" style="width:0%"></div>
                        </div>
                        <div style="display:flex; justify-content:space-between; margin-top:5px; font-size:0.9em; color:var(--text-dim)">
                            <span id="presence-total-events">0 Events</span>
                            <span>Ziel: 50+</span>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>Typische Zeiten</h2>
                    <div id="presence-typical-times">
                        <div class="stat" style="margin-bottom:10px">
                            <div class="stat-label">Mo-Fr Abgang</div>
                            <div class="stat-value" style="font-size:1.3em" id="presence-typical-departure">--:--</div>
                        </div>
                        <div class="stat" style="margin-bottom:10px">
                            <div class="stat-label">Mo-Fr Rueckkehr</div>
                            <div class="stat-value" style="font-size:1.3em" id="presence-typical-return">--:--</div>
                        </div>
                    </div>

                    <div style="margin-top:20px; padding-top:15px; border-top:1px solid var(--border)">
                        <div class="stat-label" style="margin-bottom:10px">Kategorien-Verteilung</div>
                        <div style="display:flex; gap:10px; flex-wrap:wrap">
                            <span class="badge badge-info">Work: <span id="presence-cat-work">0</span></span>
                            <span class="badge badge-success">Short: <span id="presence-cat-short">0</span></span>
                            <span class="badge" style="background:#636e72; color:#fff">Micro: ignored</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <!-- END PRESENCE TAB -->

        <div id="tab-connections" class="tab-content">
            <div class="grid grid-full">
                <div class="card">
                    <h2>Active Proxy Connections</h2>
                    <div class="stats" style="grid-template-columns: repeat(4, 1fr); margin-bottom:20px">
                        <div class="stat">
                            <div class="stat-label">Active Now</div>
                            <div class="stat-value good" id="conn-active">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Total Sessions</div>
                            <div class="stat-value" id="conn-total">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Data Transfer</div>
                            <div class="stat-value" id="conn-data">0 MB</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Avg per Session</div>
                            <div class="stat-value" id="conn-avg">0 KB</div>
                        </div>
                    </div>

                    <div id="connection-list" class="connection-list">
                        <div class="empty-state">Keine aktiven Verbindungen</div>
                    </div>
                </div>
            </div>
        </div>

        <div id="tab-system" class="tab-content">
            <div class="grid">
                <div class="card">
                    <h2>CPU Governor</h2>
                    <div class="stat">
                        <div class="stat-label">Current Governor</div>
                        <div class="stat-value" style="font-size:1.3em" id="current-governor">...</div>
                    </div>

                    <h3 style="margin-top:25px; margin-bottom:15px; color:var(--accent)">Available Governors</h3>
                    <div id="governor-buttons" class="buttons">
                        </div>
                </div>

                <div class="card">
                    <h2>System Metrics</h2>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-label">CPU Temperature</div>
                            <div class="stat-value" id="cpu-temp">--C</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">CPU Usage</div>
                            <div class="stat-value" id="cpu-usage">--%</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">RAM Usage</div>
                            <div class="stat-value" id="ram-usage">--%</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Devices Online</div>
                            <div class="stat-value" id="devices-online">0</div>
                        </div>
                    </div>
                    <div id="device-list-container" style="margin-top:15px; padding-top:15px; border-top:1px solid #333">
                    </div>
                </div>
            </div>
        </div>

        <div id="tab-goals" class="tab-content">
            <div class="grid">
                <div class="card">
                    <h2>Energy Saving</h2>
                    <div class="progress-bar">
                        <div id="goal-energy-bar" class="progress-fill" style="width:0%"></div>
                    </div>
                    <div style="text-align:right; margin-top:5px; color:var(--text-dim)" id="goal-energy-pct">0%</div>
                    <div class="stats" style="margin-top:15px">
                        <div class="stat">
                            <div class="stat-label">Weight</div>
                            <div class="stat-value" style="font-size:1.2em" id="goal-energy-weight">40%</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Utility</div>
                            <div class="stat-value" id="goal-energy-util">0.0</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>Responsiveness</h2>
                    <div class="progress-bar">
                        <div id="goal-resp-bar" class="progress-fill" style="width:0%"></div>
                    </div>
                    <div style="text-align:right; margin-top:5px; color:var(--text-dim)" id="goal-resp-pct">0%</div>
                    <div class="stats" style="margin-top:15px">
                        <div class="stat">
                            <div class="stat-label">Weight</div>
                            <div class="stat-value" style="font-size:1.2em" id="goal-resp-weight">30%</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Utility</div>
                            <div class="stat-value" id="goal-resp-util">0.0</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>Stability</h2>
                    <div class="progress-bar">
                        <div id="goal-stab-bar" class="progress-fill" style="width:0%"></div>
                    </div>
                    <div style="text-align:right; margin-top:5px; color:var(--text-dim)" id="goal-stab-pct">0%</div>
                    <div class="stats" style="margin-top:15px">
                        <div class="stat">
                            <div class="stat-label">Weight</div>
                            <div class="stat-value" style="font-size:1.2em" id="goal-stab-weight">20%</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Utility</div>
                            <div class="stat-value" id="goal-stab-util">0.0</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>Learning & Curiosity</h2>
                    <div class="progress-bar">
                        <div id="goal-learn-bar" class="progress-fill" style="width:0%"></div>
                    </div>
                    <div style="text-align:right; margin-top:5px; color:var(--text-dim)" id="goal-learn-pct">0%</div>
                    <div class="stats" style="margin-top:15px">
                        <div class="stat">
                            <div class="stat-label">Curiosity Gain</div>
                            <div class="stat-value" style="font-size:1.2em" id="goal-curiosity-gain">0.0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Total Learning Utility</div>
                            <div class="stat-value" id="goal-learn-util">0.0</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div id="tab-skills" class="tab-content">
            <div class="grid grid-full">
                <div class="card">
                    <h2>Skills Management</h2>
                    <div id="skills-list">
                        </div>
                </div>
            </div>
        </div>

        <div id="tab-learning" class="tab-content">
            <div class="grid">
                <div class="card">
                    <h2>Bayesian Learning</h2>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-label">Total Observations</div>
                            <div class="stat-value" id="bayesian-obs">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Prior Probability</div>
                            <div class="stat-value" id="bayesian-prior">30%</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Current Learning Rate</div>
                            <div class="stat-value" style="font-size:1.2em" id="learning-rate">0.05</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Current Zone</div>
                            <div class="stat-value" style="font-size:1.2em" id="current-zone-display">unknown</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>A/B Testing</h2>
                    <div id="ab-tests">
                        </div>
                </div>

                <div class="card">
                    <h2>GOAP Planner</h2>
                    <div class="stat">
                        <div class="stat-label">Current Plan</div>
                        <div class="stat-value" style="font-size:1em" id="goap-plan">No plan</div>
                    </div>
                    <div class="stat" style="margin-top:15px">
                        <div class="stat-label">Progress</div>
                        <div class="stat-value" id="goap-progress">0/0</div>
                    </div>
                </div>

                <div class="card">
                    <h2>MCDM Governor</h2>
                    <div id="mcdm-scores">
                        </div>
                </div>
            </div>
        </div>

        <div id="tab-logs" class="tab-content">
            <div class="card">
                <h2>System Live Logs</h2>
                <div id="log-container" class="log-console">
                    </div>
            </div>
        </div>

        <!-- ERRORS TAB -->
        <div id="tab-errors" class="tab-content">
            <div class="grid">
                <div class="card">
                    <h2>Error Statistiken</h2>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-label">Gesamt Errors</div>
                            <div class="stat-value crit" id="error-total">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Letzte Stunde</div>
                            <div class="stat-value warn" id="error-last-hour">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Kritisch</div>
                            <div class="stat-value crit" id="error-critical">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Warnungen</div>
                            <div class="stat-value warn" id="error-warnings">0</div>
                        </div>
                    </div>
                    <div style="margin-top:20px">
                        <h3 style="color:var(--accent); margin-bottom:10px">Haeufigste Fehler</h3>
                        <div id="error-common-list" style="font-size:0.9em; color:var(--text-dim)">
                            Keine Fehler
                        </div>
                    </div>
                    <div class="buttons" style="margin-top:20px">
                        <button class="btn btn-warning" onclick="clearErrors()">Errors loeschen</button>
                    </div>
                </div>

                <div class="card">
                    <h2>Fehler nach Modul</h2>
                    <div id="error-by-module" style="max-height:300px; overflow-y:auto">
                        <div class="empty-state">Keine Fehler</div>
                    </div>
                </div>
            </div>

            <div class="grid grid-full" style="margin-top:20px">
                <div class="card">
                    <h2>Letzte Fehler</h2>
                    <div id="error-list" class="log-console" style="height:400px">
                        <div class="empty-state">Keine Fehler aufgezeichnet</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- RAM MANAGEMENT TAB -->
        <div id="tab-ram" class="tab-content">
            <div class="grid">
                <div class="card">
                    <h2>RAM Nutzung</h2>
                    <div id="ram-status" class="status-display status-online">OK</div>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-label">Gesamt RAM</div>
                            <div class="stat-value" id="ram-total">0 MB</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Verfuegbar</div>
                            <div class="stat-value good" id="ram-available">0 MB</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Genutzt</div>
                            <div class="stat-value" id="ram-used">0 MB</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Auslastung</div>
                            <div class="stat-value" id="ram-percent">0%</div>
                        </div>
                    </div>
                    <div style="margin-top:15px">
                        <div class="stat-label">RAM Auslastung</div>
                        <div class="progress-bar">
                            <div id="ram-bar" class="progress-fill" style="width:0%"></div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>Cache Status</h2>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-label">Items im Cache</div>
                            <div class="stat-value" id="cache-items">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Cache Groesse</div>
                            <div class="stat-value" id="cache-size">0 MB</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Items auf Disk</div>
                            <div class="stat-value" id="disk-items">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Hit Rate</div>
                            <div class="stat-value good" id="cache-hit-rate">0%</div>
                        </div>
                    </div>
                    <div style="margin-top:15px">
                        <div class="stat-label">Cache Auslastung</div>
                        <div class="progress-bar">
                            <div id="cache-bar" class="progress-fill" style="width:0%"></div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>Operationen</h2>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-label">Stores</div>
                            <div class="stat-value" id="ram-stores">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Retrieves</div>
                            <div class="stat-value" id="ram-retrieves">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Ausgelagert</div>
                            <div class="stat-value" id="ram-offloads">0</div>
                        </div>
                        <div class="stat">
                            <div class="stat-label">Von Disk geladen</div>
                            <div class="stat-value" id="ram-disk-loads">0</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>Aktionen</h2>
                    <div class="buttons">
                        <button class="btn btn-primary" onclick="triggerRamCleanup()">Cache leeren</button>
                        <button class="btn btn-warning" onclick="triggerDiskCleanup()">Alte Disk-Daten loeschen</button>
                    </div>
                    <p style="color:var(--text-dim); margin-top:15px; font-size:0.9em">
                        Der RAM-Manager lagert automatisch ungenutzte Daten auf die SD-Karte aus,
                        wenn die RAM-Auslastung zu hoch wird. Ein Index im RAM ermoeglicht schnellen Zugriff.
                    </p>
                </div>
            </div>
        </div>

        <!-- SKILL_CONTENT_PLACEHOLDER -->


    </div>

    <script>
        // Configuration
        const UPDATE_INTERVAL = 2000; // 2 seconds

        let currentTab = 'overview';

        // Show Tab
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));

            document.getElementById('tab-' + tabName).classList.add('active');

            // Fix: Find the button that was clicked and activate it
            const buttons = document.getElementsByClassName('tab');
            for(let btn of buttons) {
                if(btn.innerText.includes(tabName.replace('-', ' ').toUpperCase()) ||
                   btn.getAttribute('onclick').includes(tabName)) {
                    btn.classList.add('active');
                }
            }

            currentTab = tabName;
        }

        // Send Action
        function sendAction(action) {
            fetch(`/api/action?action=${action}`, { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        showToast(`Action: ${action}`, 'success');
                    } else {
                        showToast(`Failed: ${data.message || 'Unknown error'}`, 'error');
                    }
                })
                .catch(e => {
                    console.error('Action error:', e);
                    showToast('Network error', 'error');
                });
        }

        // Toggle Skill
        function toggleSkill(skillName, enabled) {
            const action = enabled ? 'enable' : 'disable';
            fetch(`/api/skill/${action}?name=${skillName}`, { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        showToast(`Skill ${skillName}: ${action}d`, 'success');
                    }
                })
                .catch(e => console.error('Skill toggle error:', e));
        }

        // Set Governor
        function setGovernor(gov) {
            fetch(`/api/action?action=set_governor_${gov}`, { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        showToast(`Governor set to: ${gov}`, 'success');
                    }
                })
                .catch(e => console.error('Governor error:', e));
        }

        // Show Toast
        function showToast(message, type = 'info') {
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.textContent = message;
            document.body.appendChild(toast);

            setTimeout(() => toast.remove(), 3000);
        }

        // Format helpers
        function formatTime(timestamp) {
            if (!timestamp) return '--';
            const mins = Math.floor((Date.now()/1000 - timestamp) / 60);
            if (mins < 1) return 'jetzt';
            if (mins < 60) return mins + 'm';
            const hours = Math.floor(mins / 60);
            if (hours < 24) return hours + 'h';
            return Math.floor(hours / 24) + 'd';
        }

        function formatBytes(bytes) {
            if (bytes < 1024) return bytes + ' B';
            if (bytes < 1024*1024) return (bytes/1024).toFixed(1) + ' KB';
            return (bytes/(1024*1024)).toFixed(2) + ' MB';
        }

        function formatDuration(seconds) {
            if (seconds < 60) return seconds.toFixed(0) + 's';
            if (seconds < 3600) return (seconds/60).toFixed(1) + 'm';
            return (seconds/3600).toFixed(1) + 'h';
        }

        // Update UI
        function updateUI() {
            fetch('/api/state')
                .then(r => r.json())
                .then(data => {
                    updateOverview(data);
                    updateNAS(data);
                    updateConnections(data);
                    updateSystem(data);
                    updateGoals(data);
                    updateSkills(data);
                    updateLearning(data);
                    updateAILearning(data);
                    updatePresence(data);
                    updateLogs(data.logs);
                    updateEvents(data);
                    updateErrors(data);
                    updateRAM(data);
                })
                .catch(e => console.error('Update error:', e));
        }

        // ============ ERROR TAB UPDATE ============
        function updateErrors(data) {
            const errors = data.errors || {};
            const stats = errors.statistics || {};

            // Statistiken
            document.getElementById('error-total').textContent = stats.total_errors || 0;
            document.getElementById('error-last-hour').textContent = stats.errors_last_hour || 0;
            document.getElementById('error-critical').textContent = errors.critical_count || 0;
            document.getElementById('error-warnings').textContent = errors.warning_count || 0;

            // Haeufigste Fehler
            const commonList = document.getElementById('error-common-list');
            if (stats.most_common && stats.most_common.length > 0) {
                let html = '<ul style="list-style:none; padding:0">';
                stats.most_common.forEach(item => {
                    html += `<li style="margin-bottom:5px">
                        <span class="badge badge-danger">${item.count}x</span>
                        <span style="margin-left:10px">${item.error.substring(0, 60)}...</span>
                    </li>`;
                });
                html += '</ul>';
                commonList.innerHTML = html;
            } else {
                commonList.innerHTML = 'Keine Fehler';
            }

            // Fehler nach Modul
            const byModule = document.getElementById('error-by-module');
            if (stats.errors_by_module && Object.keys(stats.errors_by_module).length > 0) {
                let html = '';
                Object.entries(stats.errors_by_module).forEach(([module, count]) => {
                    html += `<div class="skill-item">
                        <span class="skill-name">${module}</span>
                        <span class="badge badge-danger">${count}</span>
                    </div>`;
                });
                byModule.innerHTML = html;
            } else {
                byModule.innerHTML = '<div class="empty-state">Keine Fehler</div>';
            }

            // Error Liste
            const errorList = document.getElementById('error-list');
            const recentErrors = errors.recent_errors || [];
            if (recentErrors.length > 0) {
                let html = '';
                recentErrors.forEach(err => {
                    const severityClass = err.severity === 'critical' ? 'log-ERROR' :
                                          err.severity === 'error' ? 'log-ERROR' :
                                          err.severity === 'warning' ? 'log-WARNING' : 'log-INFO';
                    html += `<div class="log-entry ${severityClass}">
                        <span class="log-time">[${err.timestamp.substring(11, 19)}]</span>
                        <strong>[${err.module}]</strong> ${err.error_type}: ${err.message}
                        ${err.count > 1 ? `<span class="badge badge-warning" style="margin-left:10px">${err.count}x</span>` : ''}
                    </div>`;
                });
                errorList.innerHTML = html;
            } else {
                errorList.innerHTML = '<div class="empty-state">Keine Fehler aufgezeichnet</div>';
            }
        }

        function clearErrors() {
            fetch('/api/action?action=clear_errors', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        showToast('Errors geloescht', 'success');
                    }
                })
                .catch(e => console.error('Clear errors failed:', e));
        }

        // ============ RAM TAB UPDATE ============
        function updateRAM(data) {
            const ram = data.ram_manager || {};
            const ramStats = ram.ram || {};
            const cache = ram.cache || {};
            const ops = ram.operations || {};

            // RAM Status
            const ramPercent = ramStats.percent_used || 0;
            const ramStatus = document.getElementById('ram-status');
            if (ramPercent > 90) {
                ramStatus.textContent = 'KRITISCH';
                ramStatus.className = 'status-display status-offline';
            } else if (ramPercent > 75) {
                ramStatus.textContent = 'WARNUNG';
                ramStatus.className = 'status-display status-busy';
            } else {
                ramStatus.textContent = 'OK';
                ramStatus.className = 'status-display status-online';
            }

            // RAM Werte
            document.getElementById('ram-total').textContent = (ramStats.total_mb || 0).toFixed(0) + ' MB';
            document.getElementById('ram-available').textContent = (ramStats.available_mb || 0).toFixed(0) + ' MB';
            document.getElementById('ram-used').textContent = (ramStats.used_mb || 0).toFixed(0) + ' MB';
            document.getElementById('ram-percent').textContent = ramPercent.toFixed(1) + '%';

            // RAM Bar
            const ramBar = document.getElementById('ram-bar');
            ramBar.style.width = ramPercent + '%';
            ramBar.style.background = ramPercent > 90 ? 'var(--danger)' :
                                      ramPercent > 75 ? 'var(--warning)' :
                                      'linear-gradient(90deg, var(--accent), var(--success))';

            // Cache Werte
            document.getElementById('cache-items').textContent = cache.items || 0;
            document.getElementById('cache-size').textContent = (cache.size_mb || 0).toFixed(1) + ' MB';
            document.getElementById('disk-items').textContent = (ram.index || {}).on_disk || 0;
            document.getElementById('cache-hit-rate').textContent = (ram.cache_hit_rate || 0).toFixed(1) + '%';

            // Cache Bar
            const cacheUtil = (cache.utilization || 0) * 100;
            document.getElementById('cache-bar').style.width = cacheUtil + '%';

            // Operationen
            document.getElementById('ram-stores').textContent = ops.stores || 0;
            document.getElementById('ram-retrieves').textContent = ops.retrieves || 0;
            document.getElementById('ram-offloads').textContent = ops.offloads || 0;
            document.getElementById('ram-disk-loads').textContent = ops.loads_from_disk || 0;
        }

        function triggerRamCleanup() {
            fetch('/api/action?action=ram_cleanup', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        showToast('Cache geleert', 'success');
                    }
                })
                .catch(e => console.error('RAM cleanup failed:', e));
        }

        function triggerDiskCleanup() {
            fetch('/api/action?action=disk_cleanup', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        showToast('Alte Disk-Daten geloescht', 'success');
                    }
                })
                .catch(e => console.error('Disk cleanup failed:', e));
        }


        function updateOverview(data) {
            const s = data.state;
            const d = data.decision;

            // Header stats
            document.getElementById('total-utility').textContent =
                (d.total_utility * 100).toFixed(0) + '%';
            document.getElementById('observations-count').textContent =
                data.probabilistic.total_observations;
            document.getElementById('active-tests').textContent =
                Object.keys(data.ab_tests || {}).length;

            // NAS Status Quick
            const nasStatus = s.nas_status.online ?
                (s.nas_status.state === 'busy' ? 'BUSY' :
                 s.nas_status.state === 'idle' ? 'IDLE' : 'ONLINE') :
                'OFFLINE';

            const statusElem = document.getElementById('nas-status-quick');
            statusElem.textContent = nasStatus;
            statusElem.className = 'status-display status-' +
                (nasStatus === 'OFFLINE' ? 'offline' :
                 nasStatus === 'BUSY' ? 'busy' :
                 nasStatus === 'IDLE' ? 'idle' : 'online');

            document.getElementById('nas-state-quick').textContent = s.nas_status.state;
            document.getElementById('nas-load-quick').textContent =
                (s.nas_status.load * 100).toFixed(0) + '%';
            document.getElementById('nas-conn-quick').textContent = s.nas_status.connections;
            document.getElementById('nas-idle-quick').textContent =
                Math.floor((Date.now()/1000 - s.last_activity_ts) / 60) + 'm';

            // System Health Quick
            const temp = s.system_metrics.cpu_temp;
            const tempElem = document.getElementById('cpu-temp-quick');
            tempElem.textContent = temp.toFixed(1) + 'C';
            tempElem.className = 'stat-value';
            if (temp >= 75) tempElem.classList.add('crit');
            else if (temp >= 65) tempElem.classList.add('warn');
            else tempElem.classList.add('good');

            document.getElementById('cpu-usage-quick').textContent =
                s.system_metrics.cpu_usage.toFixed(1) + '%';
            document.getElementById('ram-usage-quick').textContent =
                s.system_metrics.ram_usage.toFixed(1) + '%';
            document.getElementById('governor-quick').textContent = s.current_governor;

            // Decision Status
            document.getElementById('last-decision').textContent =
                d.last_decision || 'None';
            document.getElementById('current-plan').textContent =
                d.current_plan.length > 0 ? d.current_plan.join(' -> ') : 'No active plan';
        }

        function updateNAS(data) {
            const s = data.state;
            const p = data.probabilistic;

            // Full Status
            const nasStatus = s.nas_status.online ?
                (s.nas_status.state === 'busy' ? 'BUSY' :
                 s.nas_status.state === 'idle' ? 'IDLE' : 'ONLINE') :
                'OFFLINE';

            const statusElem = document.getElementById('nas-status-full');
            statusElem.textContent = nasStatus;
            statusElem.className = 'status-display status-' +
                (nasStatus === 'OFFLINE' ? 'offline' :
                 nasStatus === 'BUSY' ? 'busy' :
                 nasStatus === 'IDLE' ? 'idle' : 'online');

            document.getElementById('nas-ip').textContent = data.config.nas.ip;
            document.getElementById('nas-state').textContent = s.nas_status.state;
            document.getElementById('nas-load').textContent =
                (s.nas_status.load * 100).toFixed(0) + '%';
            document.getElementById('nas-connections').textContent = s.nas_status.connections;
            document.getElementById('nas-cpu').textContent =
                (s.nas_status.cpu || 0).toFixed(1) + '%';
            document.getElementById('nas-ram').textContent =
                (s.nas_status.ram || 0).toFixed(1) + '%';

            // Statistics
            document.getElementById('total-wol').textContent = s.total_wol || 0;
            document.getElementById('total-shutdowns').textContent = s.total_shutdowns || 0;

            const idleMins = Math.floor((Date.now()/1000 - s.last_activity_ts) / 60);
            document.getElementById('idle-time').textContent = idleMins + 'm';
            document.getElementById('last-activity').textContent = formatTime(s.last_activity_ts);

            // Probability
            const prob = p.probability * 100;
            document.getElementById('nas-prob-bar').style.width = prob + '%';
            document.getElementById('nas-prob-pct').textContent = prob.toFixed(1) + '%';
        }

        function updateConnections(data) {
            const conns = data.connections || [];
            const stats = data.proxy_stats;

            // Stats
            document.getElementById('conn-active').textContent = conns.length;
            document.getElementById('conn-total').textContent = stats.total_connections;
            document.getElementById('conn-data').textContent = stats.total_data_mb.toFixed(2) + ' MB';

            const avgKB = stats.total_connections > 0 ?
                (stats.total_data_mb * 1024) / stats.total_connections : 0;
            document.getElementById('conn-avg').textContent = avgKB.toFixed(1) + ' KB';

            // Connection List
            const container = document.getElementById('connection-list');

            if (conns.length === 0) {
                container.innerHTML = '<div class="empty-state">Keine aktiven Verbindungen</div>';
                return;
            }

            let html = '';
            conns.forEach(conn => {
                const totalBytes = conn.bytes_sent + conn.bytes_received;
                html += `
                    <div class="connection-item">
                        <div class="connection-header">
                            <div class="connection-ip">${conn.client_ip}:${conn.client_port}</div>
                            <span class="badge badge-success">ACTIVE</span>
                        </div>
                        <div class="connection-details">
                            <div class="connection-detail">
                                <span class="connection-detail-label">Target Port</span>
                                <span class="connection-detail-value">${conn.target_port}</span>
                            </div>
                            <div class="connection-detail">
                                <span class="connection-detail-label">Duration</span>
                                <span class="connection-detail-value">${formatDuration(conn.duration)}</span>
                            </div>
                            <div class="connection-detail">
                                <span class="connection-detail-label">Data Transfer</span>
                                <span class="connection-detail-value">${formatBytes(totalBytes)}</span>
                            </div>
                        </div>
                    </div>
                `;
            });

            container.innerHTML = html;
        }

        function updateSystem(data) {
            const s = data.state;

            // Current Governor
            document.getElementById('current-governor').textContent = s.current_governor;

            // Metrics
            const temp = s.system_metrics.cpu_temp;
            const tempElem = document.getElementById('cpu-temp');
            tempElem.textContent = temp.toFixed(1) + 'C';
            tempElem.className = 'stat-value';
            if (temp >= 75) tempElem.classList.add('crit');
            else if (temp >= 65) tempElem.classList.add('warn');
            else tempElem.classList.add('good');

            document.getElementById('cpu-usage').textContent =
                s.system_metrics.cpu_usage.toFixed(1) + '%';
            document.getElementById('ram-usage').textContent =
                s.system_metrics.ram_usage.toFixed(1) + '%';
            document.getElementById('devices-online').textContent = s.devices_online;

            // Device list
            const deviceStatus = s.device_status || {};
            const onlineDevices = Object.keys(deviceStatus)
                .filter(key => deviceStatus[key] === true)
                .map(key => key.replace('_online', '').replace(/_/g, ' '));

            const deviceListContainer = document.getElementById('device-list-container');
            if (onlineDevices.length > 0) {
                deviceListContainer.innerHTML = onlineDevices.map(d =>
                    `<span class="badge badge-success" style="margin-right:5px; margin-bottom:5px; display:inline-block">${d}</span>`
                ).join('');
            } else {
                deviceListContainer.innerHTML = '<span style="color:var(--text-dim)">Keine Geraete online</span>';
            }

            // Governor Buttons (only once)
            if (!window.governorButtonsCreated) {
                const govContainer = document.getElementById('governor-buttons');
                const govs = data.config.cpu_governors.available;

                govContainer.innerHTML = govs.map(gov =>
                    `<button class="btn btn-primary" onclick="setGovernor('${gov}')">${gov}</button>`
                ).join('');

                window.governorButtonsCreated = true;
            }
        }

        function updateGoals(data) {
            const goals = data.goals || {};

            // Energy
            if (goals.energy_saving) {
                const sat = goals.energy_saving.satisfaction * 100;
                document.getElementById('goal-energy-bar').style.width = sat + '%';
                document.getElementById('goal-energy-pct').textContent = sat.toFixed(0) + '%';
                document.getElementById('goal-energy-weight').textContent =
                    (goals.energy_saving.weight * 100).toFixed(0) + '%';
                document.getElementById('goal-energy-util').textContent =
                    goals.energy_saving.utility.toFixed(3);
            }

            // Responsiveness
            if (goals.responsiveness) {
                const sat = goals.responsiveness.satisfaction * 100;
                document.getElementById('goal-resp-bar').style.width = sat + '%';
                document.getElementById('goal-resp-pct').textContent = sat.toFixed(0) + '%';
                document.getElementById('goal-resp-weight').textContent =
                    (goals.responsiveness.weight * 100).toFixed(0) + '%';
                document.getElementById('goal-resp-util').textContent =
                    goals.responsiveness.utility.toFixed(3);
            }

            // Stability
            if (goals.stability) {
                const sat = goals.stability.satisfaction * 100;
                document.getElementById('goal-stab-bar').style.width = sat + '%';
                document.getElementById('goal-stab-pct').textContent = sat.toFixed(0) + '%';
                document.getElementById('goal-stab-weight').textContent =
                    (goals.stability.weight * 100).toFixed(0) + '%';
                document.getElementById('goal-stab-util').textContent =
                    goals.stability.utility.toFixed(3);
            }

            // Learning & Curiosity
            if (goals.learning && goals.curiosity) {
                const sat = goals.learning.satisfaction * 100;
                document.getElementById('goal-learn-bar').style.width = sat + '%';
                document.getElementById('goal-learn-pct').textContent = sat.toFixed(0) + '%';
                document.getElementById('goal-curiosity-gain').textContent =
                    goals.curiosity.current.toFixed(3);
                document.getElementById('goal-learn-util').textContent =
                    (goals.learning.utility + goals.curiosity.utility).toFixed(3);
            }
        }

        function updateSkills(data) {
            const skills = data.skills || [];
            const container = document.getElementById('skills-list');

            if (skills.length === 0) {
                container.innerHTML = '<div class="empty-state">No skills available</div>';
                return;
            }

            let html = '';
            skills.forEach(skill => {
                html += `
                    <div class="skill-item">
                        <div class="skill-name">${skill.name}</div>
                        <label class="skill-toggle">
                            <input type="checkbox" ${skill.enabled ? 'checked' : ''}
                                   onchange="toggleSkill('${skill.name}', this.checked)">
                            <span class="skill-toggle-slider"></span>
                        </label>
                    </div>
                `;
            });

            if(container.childElementCount !== skills.length || container.innerHTML.includes('No skills')) {
                 container.innerHTML = html;
            }
        }

        function updateLearning(data) {
            const s = data.state;
            const p = data.probabilistic;
            const ab = data.ab_tests || {};
            const d = data.decision;

            // Bayesian
            document.getElementById('bayesian-obs').textContent = p.total_observations;
            document.getElementById('bayesian-prior').textContent =
                (p.probability * 100).toFixed(0) + '%';
            document.getElementById('learning-rate').textContent =
                p.learning_rate.toFixed(3);
            document.getElementById('current-zone-display').textContent =
                s.current_zone;

            // A/B Tests
            const abContainer = document.getElementById('ab-tests');
            const testNames = Object.keys(ab);

            if (testNames.length === 0) {
                abContainer.innerHTML = '<div class="empty-state">No active tests</div>';
            } else {
                let html = '';
                testNames.forEach(name => {
                    html += `<div class="stat"><div class="stat-label">${name}</div>
                             <div class="stat-value" style="font-size:1em">Active</div></div>`;
                });
                abContainer.innerHTML = html;
            }

            // GOAP
            document.getElementById('goap-plan').textContent =
                d.current_plan.length > 0 ? d.current_plan.join(' -> ') : 'No plan';
            document.getElementById('goap-progress').textContent = d.plan_progress;
        }

        function updateAILearning(data) {
            if (!data.ai_upgrade) return;

            const ai = data.ai_upgrade;
            const pred = data.state.ai_prediction || {};

            // Stats
            const bayesianContexts = document.getElementById('ai-bayesian-contexts');
            if (bayesianContexts) {
                bayesianContexts.textContent = ai.bayesian.contexts || 0;
            }

            const qlUpdates = document.getElementById('ai-ql-updates');
            if (qlUpdates) {
                qlUpdates.textContent = ai.universal_ql.total_updates || 0;
            }

            const totalObs = document.getElementById('ai-total-obs');
            if (totalObs) {
                totalObs.textContent = ai.total_observations || 0;
            }

            const avgQ = document.getElementById('ai-avg-q');
            if (avgQ) {
                avgQ.textContent = (ai.universal_ql.avg_q_value || 0).toFixed(3);
            }

            // Current Prediction
            const nasProb = document.getElementById('ai-nas-prob');
            if (nasProb) {
                nasProb.textContent = pred.nas_usage_prob ?
                    (pred.nas_usage_prob * 100).toFixed(1) + '%' : '-';
            }

            const recommended = document.getElementById('ai-recommended');
            if (recommended) {
                recommended.textContent = pred.recommended_action || '-';
            }

            const confidence = document.getElementById('ai-confidence');
            if (confidence) {
                confidence.textContent = pred.confidence ?
                    (pred.confidence * 100).toFixed(1) + '%' : '-';
            }
        }

        // PRESENCE UPDATE FUNCTION
        function updatePresence(data) {
            const presence = data.presence || {};
            const stats = presence.statistics || {};
            const dayMode = presence.day_mode || {};
            const prediction = data.state.presence_prediction || {};

            // Status Display
            const statusEl = document.getElementById('presence-status');
            const userHome = stats.user_is_home !== false;

            if (userHome) {
                statusEl.textContent = 'ZUHAUSE';
                statusEl.className = 'status-display status-online';
                document.getElementById('presence-user-status').textContent = 'Zuhause';
            } else {
                statusEl.textContent = 'UNTERWEGS';
                statusEl.className = 'status-display status-busy';
                document.getElementById('presence-user-status').textContent = 'Unterwegs';
            }

            // Day Mode Badge
            const mode = stats.current_day_mode || dayMode.mode || 'unknown';
            const modeDisplay = stats.day_mode_display || dayMode.display_name || 'Unbekannt';
            const modeBadge = document.getElementById('presence-mode-badge');
            const modeIcon = document.getElementById('presence-mode-icon');
            const modeText = document.getElementById('presence-mode-text');

            modeBadge.className = 'presence-mode-badge ' + mode;

            const modeIcons = {
                'work_day': 'Work',
                'free_day': 'Free',
                'weekend': 'Weekend',
                'home_office': 'Home',
                'unknown': '?'
            };

            modeIcon.textContent = modeIcons[mode] || '?';
            modeText.textContent = modeDisplay;

            document.getElementById('presence-day-mode').textContent = modeDisplay;
            document.getElementById('presence-mode-reason').textContent =
                dayMode.reasoning || '--';

            // Mode detected time
            if (dayMode.detected_at) {
                const detectedDate = new Date(dayMode.detected_at);
                document.getElementById('presence-mode-time').textContent =
                    detectedDate.toLocaleTimeString('de-DE', {hour: '2-digit', minute: '2-digit'});
            } else {
                document.getElementById('presence-mode-time').textContent = '--:--';
            }

            // Prediction Section
            const predContainer = document.getElementById('presence-prediction-container');
            const noPrediction = document.getElementById('presence-no-prediction');

            if (!userHome && prediction && prediction.expected_return_str) {
                predContainer.style.display = 'block';
                noPrediction.style.display = 'none';

                document.getElementById('presence-return-time').textContent =
                    prediction.expected_return_str || '--:--';
                document.getElementById('presence-window').textContent =
                    `Zeitfenster: ${prediction.window_early || '--'} bis ${prediction.window_late || '--'}`;

                const confidence = (prediction.confidence || 0) * 100;
                document.getElementById('presence-confidence-pct').textContent =
                    confidence.toFixed(0) + '%';

                const confBar = document.getElementById('presence-confidence-bar');
                confBar.style.width = confidence + '%';
                confBar.className = 'confidence-fill ' +
                    (confidence >= 70 ? 'high' : confidence >= 40 ? 'medium' : 'low');

                const catEmojis = {
                    'short_trip': 'Kurzer Trip',
                    'work': 'Arbeit',
                    'possibly_longer': 'Evtl. laenger'
                };
                document.getElementById('presence-category').textContent =
                    catEmojis[prediction.category] || prediction.category || '--';

                document.getElementById('presence-sample-size').textContent =
                    (prediction.sample_size || 0) + ' Events';
            } else {
                predContainer.style.display = 'none';
                noPrediction.style.display = 'block';
            }

            // Statistics
            document.getElementById('presence-work-count').textContent =
                stats.total_work_absences || 0;
            document.getElementById('presence-work-avg').textContent =
                (stats.work_avg_duration_hours || '--') + 'h';
            document.getElementById('presence-short-count').textContent =
                stats.total_short_trips || 0;
            document.getElementById('presence-short-avg').textContent =
                (stats.short_trip_avg_minutes || '--') + 'min';

            // Learning Progress Bar
            const totalEvents = (stats.total_work_absences || 0) + (stats.total_short_trips || 0);
            const learningPct = Math.min(100, (totalEvents / 50) * 100);
            document.getElementById('presence-learning-bar').style.width = learningPct + '%';
            document.getElementById('presence-total-events').textContent = totalEvents + ' Events';

            // Category badges
            document.getElementById('presence-cat-work').textContent =
                stats.total_work_absences || 0;
            document.getElementById('presence-cat-short').textContent =
                stats.total_short_trips || 0;

            // Typical times
            if (stats.typical_return_by_weekday) {
                const times = Object.values(stats.typical_return_by_weekday);
                if (times.length > 0) {
                    document.getElementById('presence-typical-return').textContent =
                        times[0] || '--:--';
                }
            }
        }
        // END PRESENCE UPDATE


        function updateLogs(logs) {
            const container = document.getElementById('log-container');
            if (!logs) return;

            let html = '';
            logs.forEach(log => {
                html += `
                    <div class="log-entry ${'log-' + log.level}">
                        <span class="log-time">[${log.time}]</span>
                        <span>${log.message.split(' - ').slice(2).join(' - ')}</span>
                    </div>
                `;
            });

            if (container.innerHTML.length !== html.length) {
                 container.innerHTML = html;
            }
        }

        function updateEvents(data) {
            const events = data.nas_events || [];
            const override = data.manual_override || {};

            // Event Liste
            const container = document.getElementById('nas-events-list');
            if (events.length === 0) {
                container.innerHTML = '<div class="empty-state">Keine Events aufgezeichnet</div>';
            } else {
                let html = '';
                [...events].reverse().forEach(event => {
                    let icon = '?';
                    let colorClass = '';

                    if (event.type.includes('wake')) {
                        icon = 'Wake';
                        colorClass = 'log-INFO';
                    } else if (event.type.includes('sleep') || event.type.includes('suspend')) {
                        icon = 'Sleep';
                        colorClass = 'log-WARNING';
                    }

                    if (event.source === 'user' || event.source === 'user_manual') {
                        icon = 'Manual ' + icon;
                    }

                    html += `
                        <div class="log-entry ${colorClass}">
                            <span class="log-time">[${event.time}]</span>
                            <span>${icon} <strong>${event.type}</strong> by ${event.source}</span>
                            ${event.details ? `<br><span style="color:#888; margin-left:80px">${event.details}</span>` : ''}
                        </div>
                    `;
                });
                container.innerHTML = html;
            }

            // Manual Override Status
            const overrideStatus = document.getElementById('override-status');
            const overrideAction = document.getElementById('override-action');
            const overrideRemaining = document.getElementById('override-remaining');

            if (override.active) {
                overrideStatus.textContent = 'AKTIV';
                overrideStatus.className = 'status-display status-busy';
                overrideAction.textContent = override.action || '-';
                const mins = Math.floor(override.remaining_seconds / 60);
                const secs = override.remaining_seconds % 60;
                overrideRemaining.textContent = `${mins}m ${secs}s`;
            } else {
                overrideStatus.textContent = 'INAKTIV';
                overrideStatus.className = 'status-display status-offline';
                overrideAction.textContent = '-';
                overrideRemaining.textContent = '-';
            }

            // Event Statistiken
            let aiWakes = 0, proxyWakes = 0, manualWakes = 0, idleSleeps = 0, awaySleeps = 0;
            events.forEach(e => {
                if (e.type.includes('wake')) {
                    if (e.source === 'ai_prediction') aiWakes++;
                    else if (e.source === 'proxy') proxyWakes++;
                    else if (e.source.includes('user') || e.source.includes('manual')) manualWakes++;
                } else if (e.type.includes('sleep')) {
                    if (e.source === 'idle_timeout') idleSleeps++;
                    else if (e.source === 'away_mode') awaySleeps++;
                }
            });

            document.getElementById('stat-ai-wakes').textContent = aiWakes;
            document.getElementById('stat-proxy-wakes').textContent = proxyWakes;
            document.getElementById('stat-manual-wakes').textContent = manualWakes;
            document.getElementById('stat-idle-sleeps').textContent = idleSleeps;
            document.getElementById('stat-away-sleeps').textContent = awaySleeps;
        }

        // Start updates
        setInterval(updateUI, UPDATE_INTERVAL);
        updateUI();
    </script>
</body>
</html>
"""


class DashboardCache:
    """Cached das fertige HTML - regeneriert nur bei Skill-Aenderungen"""

    def __init__(self):
        self._cached_html = None
        self._cached_hash = None

    def get_html(self, skill_manager) -> str:
        # Hash der aktuellen Skill-Konfiguration
        current_hash = self._get_skills_hash(skill_manager)

        # Cache Hit?
        if self._cached_html and self._cached_hash == current_hash:
            return self._cached_html

        # Cache Miss - neu generieren
        self._cached_html = self._build_html(skill_manager)
        self._cached_hash = current_hash
        logger.debug("Dashboard HTML regenerated")
        return self._cached_html

    def _get_skills_hash(self, skill_manager) -> str:
        """Hash basierend auf enabled Skills"""
        enabled = sorted([
            name for name, skill in skill_manager.skills.items()
            if skill.enabled
        ])
        return hashlib.md5(str(enabled).encode()).hexdigest()

    def _build_html(self, skill_manager) -> str:
        """Baut das HTML zusammen"""
        html_output = DASHBOARD_HTML

        new_tabs = ""
        new_content = ""

        for name, skill in skill_manager.skills.items():
            if skill.enabled:
                ui = skill.get_ui()
                if ui:
                    new_tabs += ui.get('tab', '') + "\n"
                    new_content += ui.get('content', '') + "\n"

        html_output = html_output.replace("<!-- SKILL_TABS_PLACEHOLDER -->", new_tabs)
        html_output = html_output.replace("<!-- SKILL_CONTENT_PLACEHOLDER -->", new_content)

        return html_output

    def invalidate(self):
        """Cache manuell invalidieren"""
        self._cached_html = None
        self._cached_hash = None


# Globale Instanz fuer einfachen Import
dashboard_cache = DashboardCache()

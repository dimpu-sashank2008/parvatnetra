/**
 * PARVAT NETRA • First Responder Offline Field Triage & LoRa Mesh Sync Client
 * =========================================================================
 * Provides 100% offline resilience during mountain telecommunications blackouts:
 * 1. IndexedDB persistent offline storage for field damage / casualty reports.
 * 2. Network state monitoring with automated fallback to LoRa sub-GHz radio mesh.
 * 3. Bidirectional sync engine: auto-flushes queued triage reports on reconnect.
 * 4. Sub-GHz LoRa diagnostic packet stream & burst simulation.
 * 
 * Standard: NDMA SOP 2024 / ITU-T X.1303 / LoRaWAN IN865
 * Author: PARVAT NETRA / PAHAD AI Core Engineering Team
 */

const DB_NAME = 'ParvatNetraOfflineDB';
const DB_VERSION = 2;
const STORE_REPORTS = 'offline_field_reports';

let idb = null;

// Initialize IndexedDB
function initOfflineDB() {
    return new Promise((resolve, reject) => {
        if (!window.indexedDB) {
            console.warn('[OfflineDB] IndexedDB not supported by browser. Falling back to memory storage.');
            resolve(null);
            return;
        }

        const req = indexedDB.open(DB_NAME, DB_VERSION);
        req.onupgradeneeded = (e) => {
            const db = e.target.result;
            if (!db.objectStoreNames.contains(STORE_REPORTS)) {
                const store = db.createObjectStore(STORE_REPORTS, { keyPath: 'report_id' });
                store.createIndex('sync_status', 'sync_status', { unique: false });
                store.createIndex('created_at', 'created_at', { unique: false });
            }
        };

        req.onsuccess = (e) => {
            idb = e.target.result;
            console.log('[OfflineDB] Local disaster evidence store initialized.');
            resolve(idb);
        };

        req.onerror = (e) => {
            console.error('[OfflineDB] Failed to open IndexedDB:', e.target.error);
            resolve(null);
        };
    });
}

// Store report locally in IndexedDB
function saveOfflineReport(report) {
    return new Promise((resolve, reject) => {
        if (!idb) {
            // Fallback to localStorage
            const list = JSON.parse(localStorage.getItem('parvat_offline_reports') || '[]');
            list.unshift(report);
            localStorage.setItem('parvat_offline_reports', JSON.stringify(list));
            resolve(report);
            return;
        }

        const tx = idb.transaction(STORE_REPORTS, 'readwrite');
        const store = tx.objectStore(STORE_REPORTS);
        const req = store.put(report);
        req.onsuccess = () => resolve(report);
        req.onerror = (e) => reject(e.target.error);
    });
}

// Retrieve all locally stored reports
function getOfflineReports() {
    return new Promise((resolve) => {
        if (!idb) {
            const list = JSON.parse(localStorage.getItem('parvat_offline_reports') || '[]');
            resolve(list);
            return;
        }

        const tx = idb.transaction(STORE_REPORTS, 'readonly');
        const store = tx.objectStore(STORE_REPORTS);
        const req = store.getAll();
        req.onsuccess = (e) => resolve(e.target.result || []);
        req.onerror = () => resolve([]);
    });
}

// Update report sync state
function updateOfflineReportStatus(report_id, newStatus) {
    return new Promise((resolve) => {
        if (!idb) {
            const list = JSON.parse(localStorage.getItem('parvat_offline_reports') || '[]');
            const item = list.find(r => r.report_id === report_id);
            if (item) item.sync_status = newStatus;
            localStorage.setItem('parvat_offline_reports', JSON.stringify(list));
            resolve(true);
            return;
        }

        const tx = idb.transaction(STORE_REPORTS, 'readwrite');
        const store = tx.objectStore(STORE_REPORTS);
        const getReq = store.get(report_id);
        getReq.onsuccess = () => {
            const data = getReq.result;
            if (data) {
                data.sync_status = newStatus;
                data.synced_at = new Date().toISOString();
                store.put(data);
            }
            resolve(true);
        };
        getReq.onerror = () => resolve(false);
    });
}

// Flush pending reports to gateway/cloud
async function flushPendingReports() {
    const btn = document.getElementById('btn-sync-reports');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="ph-bold ph-arrows-clockwise animate-spin"></i> Syncing...';
    }

    try {
        const allReports = await getOfflineReports();
        const pending = allReports.filter(r => r.sync_status === 'QUEUED_OFFLINE');

        if (pending.length === 0) {
            displayTriageNotification('All local field reports already synchronized with edge gateway.', 'info');
            return;
        }

        const res = await fetch('/api/edge/field-reports/sync', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reports: pending })
        });

        if (res.ok) {
            const data = await res.json();
            for (const r of pending) {
                await updateOfflineReportStatus(r.report_id, 'SYNCED_EDGE');
            }
            displayTriageNotification(`Successfully synchronized ${data.synced_count} field reports over LoRa/Edge mesh!`, 'success');
            renderTriageReportsList();
        } else {
            displayTriageNotification('Sync deferred: Edge gateway unreachable. Reports safely stored in offline queue.', 'warning');
        }
    } catch (err) {
        displayTriageNotification(`Sync error: ${err.message}. Retained in offline buffer.`, 'warning');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="ph-bold ph-arrows-clockwise"></i> Sync to Edge Mesh';
        }
    }
}

// Render reports list into UI table
async function renderTriageReportsList() {
    const container = document.getElementById('offline-reports-tbody');
    if (!container) return;

    const reports = await getOfflineReports();
    const countBadge = document.getElementById('offline-queue-count');
    if (countBadge) {
        const pendingCount = reports.filter(r => r.sync_status === 'QUEUED_OFFLINE').length;
        countBadge.innerText = `${pendingCount} PENDING`;
        countBadge.className = pendingCount > 0 
            ? 'px-2 py-0.5 text-[10px] font-mono font-bold rounded bg-amber-950 text-amber-300 border border-amber-800'
            : 'px-2 py-0.5 text-[10px] font-mono font-bold rounded bg-emerald-950/70 text-emerald-300 border border-emerald-700/60';
    }

    if (reports.length === 0) {
        container.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-xs text-slate-500 font-mono">// No field reports logged in this local session.</td></tr>`;
        return;
    }

    container.innerHTML = reports.map(r => {
        const isQueued = r.sync_status === 'QUEUED_OFFLINE';
        const badgeClass = isQueued
            ? 'bg-amber-950/80 text-amber-300 border-amber-800'
            : 'bg-emerald-950/80 text-emerald-300 border-emerald-800';
        const sevClass = r.severity === 'CRITICAL' ? 'text-red-400 font-bold' : (r.severity === 'HIGH' ? 'text-amber-400 font-bold' : 'text-slate-300');

        return `
            <tr class="border-b border-slate-800/60 hover:bg-slate-900/40 text-xs font-mono">
                <td class="py-2.5 px-3 text-sky-400 font-bold">${r.report_id}</td>
                <td class="py-2.5 px-3 text-slate-200">${r.incident_type}</td>
                <td class="py-2.5 px-3 ${sevClass}">${r.severity}</td>
                <td class="py-2.5 px-3 text-slate-400">${r.latitude.toFixed(4)}, ${r.longitude.toFixed(4)}</td>
                <td class="py-2.5 px-3 text-slate-300">${r.crack_aperture_mm > 0 ? r.crack_aperture_mm + 'mm crack' : 'Surface slump'}</td>
                <td class="py-2.5 px-3">
                    <span class="px-2 py-0.5 text-[10px] font-bold rounded border ${badgeClass}">
                        ${r.sync_status}
                    </span>
                </td>
            </tr>
        `;
    }).join('');
}

// Submit new triage report from form
async function handleTriageSubmit(e) {
    e.preventDefault();
    const typeEl = document.getElementById('triage-type');
    const sevEl = document.getElementById('triage-severity');
    const latEl = document.getElementById('triage-lat');
    const lngEl = document.getElementById('triage-lng');
    const crackEl = document.getElementById('triage-crack');
    const casEl = document.getElementById('triage-casualties');
    const notesEl = document.getElementById('triage-notes');
    const nameEl = document.getElementById('triage-responder');

    const report = {
        report_id: `RPT-FIELD-${Date.now().toString(36).toUpperCase()}`,
        incident_type: typeEl ? typeEl.value : 'SLOPE_CRACK',
        severity: sevEl ? sevEl.value : 'HIGH',
        latitude: parseFloat(latEl ? latEl.value : 27.0984) || 27.0984,
        longitude: parseFloat(lngEl ? lngEl.value : 88.4892) || 88.4892,
        crack_aperture_mm: parseFloat(crackEl ? crackEl.value : 0) || 0.0,
        casualties: parseInt(casEl ? casEl.value : 0) || 0,
        notes: notesEl ? notesEl.value.trim() : '',
        reporter_name: nameEl && nameEl.value.trim() ? nameEl.value.trim() : 'Field Patrol SDRF Unit',
        reporter_role: 'FIRST_RESPONDER',
        sync_status: 'QUEUED_OFFLINE',
        created_at: new Date().toISOString()
    };

    await saveOfflineReport(report);
    displayTriageNotification(`Report ${report.report_id} committed to local offline storage!`, 'success');
    renderTriageReportsList();

    // Reset notes
    if (notesEl) notesEl.value = '';

    // Auto-attempt sync in background
    setTimeout(flushPendingReports, 500);
}

// Display inline notification banner
function displayTriageNotification(msg, type = 'info') {
    const el = document.getElementById('triage-notification');
    if (!el) return;

    let borderCol = 'border-sky-500/50 text-sky-200 bg-sky-950/40';
    if (type === 'success') borderCol = 'border-emerald-500/50 text-emerald-200 bg-emerald-950/40';
    if (type === 'warning') borderCol = 'border-amber-500/50 text-amber-200 bg-amber-950/40';

    el.className = `p-3 rounded-lg border text-xs font-mono flex items-center gap-2 transition-all ${borderCol}`;
    el.innerHTML = `<i class="ph-bold ph-info text-sm shrink-0"></i> <span>${msg}</span>`;
    el.classList.remove('hidden');

    setTimeout(() => {
        el.classList.add('hidden');
    }, 6000);
}

// Live Sub-GHz LoRa Packet Monitor
async function refreshLoRaPackets() {
    try {
        const res = await fetch('/api/edge/mesh/packets?limit=10');
        if (!res.ok) return;
        const data = await res.json();
        const container = document.getElementById('lora-packet-stream');
        if (!container) return;

        if (!data.packets || data.packets.length === 0) {
            container.innerHTML = `<div class="text-slate-500 p-2">// Standing by for 865 MHz LoRa packet transmissions...</div>`;
            return;
        }

        container.innerHTML = data.packets.map(p => {
            return `
                <div class="p-2 border-b border-slate-900 flex items-center justify-between text-[11px] font-mono hover:bg-slate-900/50">
                    <div class="flex items-center gap-2">
                        <span class="text-sky-400 font-bold">${p.node_id}</span>
                        <span class="text-slate-500">|</span>
                        <span class="text-slate-400">Seq: #${p.sequence}</span>
                        <span class="text-slate-500">|</span>
                        <span class="text-amber-300 font-bold">${p.payload_hex || '0x4C52'}</span>
                    </div>
                    <div class="flex items-center gap-3 text-[10px]">
                        <span class="text-slate-400">RSSI: <strong class="text-slate-200">${p.rssi_dbm} dBm</strong></span>
                        <span class="text-slate-400">SNR: <strong class="text-slate-200">${p.snr_db} dB</strong></span>
                        <span class="text-slate-400">Bat: <strong class="text-emerald-400">${p.battery_pct}%</strong></span>
                        <span class="px-1.5 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-800">
                            ${p.hops === 1 ? 'Direct' : 'via Relay'}
                        </span>
                    </div>
                </div>
            `;
        }).join('');
    } catch (e) {}
}

// Simulate Emergency LoRa Packet Burst
async function simulateLoRaBurst() {
    const btn = document.getElementById('btn-sim-burst');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="ph-bold ph-broadcast animate-pulse text-amber-400"></i> Emitting LoRa RF Burst...';
    }

    try {
        const res = await fetch('/api/edge/mesh/simulate-burst?count=3', { method: 'POST' });
        if (res.ok) {
            displayTriageNotification('Simulated 3 emergency sub-GHz LoRa packets from deep gorge slope sensors!', 'success');
            await refreshLoRaPackets();
        }
    } catch (e) {
        displayTriageNotification(`Burst failed: ${e.message}`, 'warning');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="ph-bold ph-broadcast text-amber-400"></i> Simulate LoRa Emergency Burst';
        }
    }
}

// Acquire GPS coordinates for triage form
function acquireTriageGPS() {
    const latEl = document.getElementById('triage-lat');
    const lngEl = document.getElementById('triage-lng');
    const btn = document.getElementById('btn-gps-triage');

    if (!navigator.geolocation) {
        alert('Geolocation not supported by this browser.');
        return;
    }

    if (btn) btn.innerText = 'Locking GPS...';
    navigator.geolocation.getCurrentPosition(
        (pos) => {
            if (latEl) latEl.value = pos.coords.latitude.toFixed(5);
            if (lngEl) lngEl.value = pos.coords.longitude.toFixed(5);
            if (btn) btn.innerText = 'GPS Locked ✓';
            displayTriageNotification(`Acquired field coordinates: ${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)}`, 'success');
        },
        (err) => {
            if (btn) btn.innerText = 'Defaulting (NH-10)';
            if (latEl) latEl.value = '27.09840';
            if (lngEl) lngEl.value = '88.48920';
            displayTriageNotification('GPS unavailable. Applied active corridor centroid reference (NH-10 Km 48).', 'info');
        },
        { enableHighAccuracy: true, timeout: 8000 }
    );
}

// Toggle Backhaul Simulation
async function toggleCloudBackhaul() {
    try {
        const res = await fetch('/api/edge/toggle-cloud', { method: 'POST' });
        if (res.ok) {
            const data = await res.json();
            const isConn = data.is_cloud_connected;

            // Backhaul banner & card badges
            const badge = document.getElementById('backhaul-status-badge');
            const desc = document.getElementById('backhaul-desc');
            const topBadge = document.getElementById('cloud-status-badge');
            const btnText = document.getElementById('btn-toggle-cloud-text');
            const connState = document.getElementById('buf-conn-state');

            if (isConn) {
                if (badge) {
                    badge.className = 'px-2.5 py-1 rounded bg-emerald-950/70 text-emerald-300 border border-emerald-700/60 font-mono font-bold text-xs';
                    badge.innerText = 'CLOUD CONNECTED';
                }
                if (desc) desc.innerText = 'Regional fiber & satellite backhaul active. Direct cloud synchronization enabled.';
                if (topBadge) {
                    topBadge.className = 'text-[11px] text-emerald-400 font-semibold tracking-wider';
                    topBadge.textContent = '[LIVE] CLOUD CONNECTED';
                }
                if (btnText) btnText.textContent = 'नेटवर्क विच्छेद परीक्षण • Severed Backhaul Test';
                if (connState) connState.textContent = 'ONLINE';

                displayTriageNotification('Cloud backhaul restored. Flushing local edge buffers to central EOC...', 'success');
                flushPendingReports();
            } else {
                if (badge) {
                    badge.className = 'px-2.5 py-1 rounded bg-red-950 text-red-300 border border-red-800 font-mono font-bold text-xs animate-pulse';
                    badge.innerText = 'EDGE OFFLINE AUTONOMOUS';
                }
                if (desc) desc.innerText = 'Backhaul severed. Local edge gateway operating 100% autonomously over sub-GHz LoRa mesh.';
                if (topBadge) {
                    topBadge.className = 'text-[11px] text-red-400 animate-pulse font-semibold tracking-wider';
                    topBadge.textContent = '[OFFLINE] EDGE AUTONOMOUS';
                }
                if (btnText) btnText.textContent = 'क्लाउड बैकहॉल पुनः स्थापित करें • Restore Backhaul';
                if (connState) connState.textContent = 'OFFLINE (AUTONOMOUS)';

                displayTriageNotification('Telecommunications blackout simulated: Operating in pure offline autonomous mode.', 'warning');
            }

            if (typeof refreshGatewayStatus === 'function') {
                refreshGatewayStatus();
            }
        }
    } catch (e) {
        alert('Toggle error: ' + e.message);
    }
}

// Window Event Listeners for PWA
window.addEventListener('online', () => {
    displayTriageNotification('Internet connectivity detected. Initiating background sync...', 'info');
    flushPendingReports();
});

window.addEventListener('offline', () => {
    displayTriageNotification('Network disconnected. Switched to local IndexedDB offline storage & LoRa mesh.', 'warning');
});

// Initialize on DOM Ready
document.addEventListener('DOMContentLoaded', async () => {
    await initOfflineDB();
    renderTriageReportsList();
    refreshLoRaPackets();

    const form = document.getElementById('offline-triage-form');
    if (form) form.addEventListener('submit', handleTriageSubmit);

    // Periodically refresh packet monitor
    setInterval(refreshLoRaPackets, 6000);
});

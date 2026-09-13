/**
 * PARVAT NETRA — Network State Machine & Operational State Tracker
 * Version: 3.2.0
 * 
 * Formal States:
 *   - ONLINE   : Active bi-directional network connectivity; live APIs operational.
 *   - DEGRADED : Partial provider outage or slow backhaul; fallback to secondary or cached data.
 *   - OFFLINE  : Browser or network offline; operational completely from IndexedDB / Service Worker.
 *   - SYNCING  : Uploading queued field reports and reconciling geospatial packages.
 */

(function(window) {
    'use strict';

    class NetworkStateMachine {
        constructor() {
            this.STATE_ONLINE = 'ONLINE';
            this.STATE_DEGRADED = 'DEGRADED';
            this.STATE_OFFLINE = 'OFFLINE';
            this.STATE_SYNCING = 'SYNCING';

            this.currentState = navigator.onLine ? this.STATE_ONLINE : this.STATE_OFFLINE;
            this.lastSyncTime = new Date();
            this.listeners = [];
            this.heartbeatInterval = null;
            this.degradedThresholdMs = 4000;

            this._initEventListeners();
            this._startHeartbeat();
        }

        _initEventListeners() {
            window.addEventListener('online', () => {
                console.log('[NetworkState] Browser online event detected. Verifying server connectivity...');
                this.verifyConnectivity();
            });

            window.addEventListener('offline', () => {
                console.warn('[NetworkState] Browser offline event detected.');
                this.setState(this.STATE_OFFLINE, { reason: 'Browser offline' });
            });
        }

        _startHeartbeat() {
            // Heartbeat check every 30 seconds to detect silent link drops in mountain corridors
            this.heartbeatInterval = setInterval(() => {
                if (this.currentState !== this.STATE_OFFLINE && this.currentState !== this.STATE_SYNCING) {
                    this.verifyConnectivity(true);
                }
            }, 30000);
        }

        async verifyConnectivity(isBackground = false) {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.degradedThresholdMs);
            const start = performance.now();

            try {
                const res = await fetch('/api/health?t=' + Date.now(), {
                    method: 'GET',
                    signal: controller.signal,
                    cache: 'no-store'
                });
                clearTimeout(timeoutId);
                const latency = performance.now() - start;

                if (res.ok) {
                    this.lastSyncTime = new Date();
                    if (latency > 2500) {
                        this.setState(this.STATE_DEGRADED, { latencyMs: Math.round(latency) });
                    } else {
                        this.setState(this.STATE_ONLINE, { latencyMs: Math.round(latency) });
                    }
                } else {
                    this.setState(this.STATE_DEGRADED, { status: res.status });
                }
            } catch (err) {
                clearTimeout(timeoutId);
                if (err.name === 'AbortError' || !navigator.onLine) {
                    this.setState(this.STATE_OFFLINE, { error: 'Network timeout or unreachable host' });
                } else {
                    this.setState(this.STATE_DEGRADED, { error: err.message });
                }
            }
        }

        setState(newState, details = {}) {
            const previousState = this.currentState;
            this.currentState = newState;

            if (newState === this.STATE_ONLINE) {
                this.lastSyncTime = new Date();
            }

            const payload = {
                state: this.currentState,
                previousState: previousState,
                lastSyncTime: this.lastSyncTime,
                dataAgeMinutes: this.getDataAgeMinutes(),
                dataAgeFormatted: this.getDataAgeFormatted(),
                details: details
            };

            // Notify custom listeners
            this.listeners.forEach((fn) => {
                try { fn(payload); } catch(e) { console.error('[NetworkState] Listener error:', e); }
            });

            // Dispatch global DOM event
            window.dispatchEvent(new CustomEvent('parvat:network-change', { detail: payload }));

            // Update UI elements across dashboard
            this._updateUIElements(payload);
        }

        getState() {
            return this.currentState;
        }

        isOnline() {
            return this.currentState === this.STATE_ONLINE;
        }

        isOffline() {
            return this.currentState === this.STATE_OFFLINE;
        }

        isDegraded() {
            return this.currentState === this.STATE_DEGRADED;
        }

        isSyncing() {
            return this.currentState === this.STATE_SYNCING;
        }

        getLastSyncTime() {
            return this.lastSyncTime;
        }

        getDataAgeMinutes() {
            if (!this.lastSyncTime) return 0;
            const diffMs = Date.now() - this.lastSyncTime.getTime();
            return Math.max(0, Math.floor(diffMs / 60000));
        }

        getDataAgeFormatted() {
            const mins = this.getDataAgeMinutes();
            if (mins < 1) return 'Just now';
            if (mins === 1) return '1 minute ago';
            if (mins < 60) return `${mins} minutes ago`;
            const hrs = Math.floor(mins / 60);
            const remMins = mins % 60;
            return `${hrs}h ${remMins}m ago`;
        }

        formatTimeIST(date = null) {
            const d = date || this.lastSyncTime || new Date();
            return d.toLocaleTimeString('en-IN', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: false,
                timeZone: 'Asia/Kolkata'
            }) + ' IST';
        }

        subscribe(callback) {
            if (typeof callback === 'function') {
                this.listeners.push(callback);
            }
        }

        _updateUIElements(payload) {
            const netBadge = document.getElementById('system-network-status');
            const dataBadge = document.getElementById('system-data-status');
            const mapBadge = document.getElementById('system-map-status');
            const pahadBadge = document.getElementById('system-pahad-status');
            const offlineBanner = document.getElementById('system-offline-banner');
            const lastSyncText = document.getElementById('system-last-sync');
            const dataAgeText = document.getElementById('system-data-age');

            if (lastSyncText) lastSyncText.textContent = this.formatTimeIST();
            if (dataAgeText) dataAgeText.textContent = this.getDataAgeFormatted();

            if (this.currentState === this.STATE_ONLINE) {
                if (netBadge) {
                    netBadge.textContent = 'ONLINE';
                    netBadge.className = 'font-mono text-emerald-400 font-bold';
                }
                if (dataBadge) {
                    dataBadge.textContent = 'LIVE';
                    dataBadge.className = 'font-mono text-cyan-400 font-bold';
                }
                if (mapBadge) {
                    mapBadge.textContent = 'READY';
                    mapBadge.className = 'font-mono text-emerald-400 font-bold';
                }
                if (pahadBadge) {
                    pahadBadge.textContent = 'ACTIVE';
                    pahadBadge.className = 'font-mono text-emerald-400 font-bold';
                }
                if (offlineBanner) offlineBanner.classList.add('hidden');
            } else if (this.currentState === this.STATE_SYNCING) {
                if (netBadge) {
                    netBadge.textContent = 'SYNCING';
                    netBadge.className = 'font-mono text-sky-400 font-bold animate-pulse';
                }
                if (dataBadge) {
                    dataBadge.textContent = 'RECONCILING';
                    dataBadge.className = 'font-mono text-sky-400 font-bold';
                }
                if (offlineBanner) offlineBanner.classList.add('hidden');
            } else if (this.currentState === this.STATE_DEGRADED) {
                if (netBadge) {
                    netBadge.textContent = 'DEGRADED';
                    netBadge.className = 'font-mono text-amber-400 font-bold';
                }
                if (dataBadge) {
                    dataBadge.textContent = 'FALLBACK / CACHED';
                    dataBadge.className = 'font-mono text-amber-400 font-bold';
                }
                if (mapBadge) {
                    mapBadge.textContent = 'READY';
                    mapBadge.className = 'font-mono text-emerald-400 font-bold';
                }
                if (pahadBadge) {
                    pahadBadge.textContent = 'DEGRADED / LAST KNOWN';
                    pahadBadge.className = 'font-mono text-amber-400 font-bold';
                }
                if (offlineBanner) {
                    offlineBanner.classList.remove('hidden');
                    offlineBanner.querySelector('.offline-msg').textContent = 
                        `DEGRADED BACKHAUL: Operating on cached satellite & weather telemetry. Last synchronized: ${this.formatTimeIST()} (${this.getDataAgeFormatted()})`;
                }
            } else {
                // OFFLINE
                if (netBadge) {
                    netBadge.textContent = 'OFFLINE';
                    netBadge.className = 'font-mono text-rose-400 font-bold';
                }
                if (dataBadge) {
                    dataBadge.textContent = 'CACHED';
                    dataBadge.className = 'font-mono text-rose-400 font-bold';
                }
                if (mapBadge) {
                    mapBadge.textContent = 'OFFLINE READY';
                    mapBadge.className = 'font-mono text-amber-400 font-bold';
                }
                if (pahadBadge) {
                    pahadBadge.textContent = 'LAST KNOWN';
                    pahadBadge.className = 'font-mono text-amber-400 font-bold';
                }
                if (offlineBanner) {
                    offlineBanner.classList.remove('hidden');
                    const msgEl = offlineBanner.querySelector('.offline-msg');
                    if (msgEl) {
                        msgEl.textContent = 
                            `OFFLINE MODE: Operating on pre-bundled operational map & cached telemetry. Last synchronized: ${this.formatTimeIST()} (${this.getDataAgeFormatted()})`;
                    }
                }
            }
        }
    }

    // Export globally
    window.ParvatNetworkState = new NetworkStateMachine();

})(window);

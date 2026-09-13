/**
 * PARVAT NETRA — IndexedDB Local Storage Layer (local_store.js)
 * Version: 5.4.0 (Phase 5D)
 * 
 * High-performance, quota-resilient structured browser storage for:
 * - PAHAD prediction snapshots (Phase 5B/5C canonical schema)
 * - Weather observations & telemetry
 * - Seismic activity records
 * - Alert history & CAP v1.2 messages with automatic expiry tracking
 * - Pre-bundled & downloaded offline map packages
 * - Field reports sync queue with 4-state lifecycle
 * - User preferences & active language
 * - Versioned schema migration support (v1 -> v2)
 */

(function(window) {
    'use strict';

    const DB_NAME = 'parvat_netra_db';
    const DB_VERSION = 2; // Upgraded for Phase 5D migrations

    class LocalDataStore {
        constructor() {
            this.db = null;
            this.readyPromise = this._initDatabase();
        }

        _initDatabase() {
            return new Promise((resolve, reject) => {
                if (!window.indexedDB) {
                    console.error('[LocalStore] IndexedDB not supported in this browser context.');
                    return resolve(null);
                }

                const request = window.indexedDB.open(DB_NAME, DB_VERSION);

                request.onupgradeneeded = (event) => {
                    const db = event.target.result;
                    const oldVersion = event.oldVersion;
                    console.log(`[LocalStore] Upgrading IndexedDB from version ${oldVersion} to ${DB_VERSION}`);

                    // 1. PAHAD Snapshots
                    let snapStore;
                    if (!db.objectStoreNames.contains('pahad_snapshots')) {
                        snapStore = db.createObjectStore('pahad_snapshots', { keyPath: 'sector_id' });
                    } else {
                        snapStore = event.target.transaction.objectStore('pahad_snapshots');
                    }
                    if (snapStore && !snapStore.indexNames.contains('timestamp')) {
                        snapStore.createIndex('timestamp', 'timestamp', { unique: false });
                    }

                    // 2. Weather Cache
                    if (!db.objectStoreNames.contains('weather_cache')) {
                        db.createObjectStore('weather_cache', { keyPath: 'id' });
                    }

                    // 3. Seismic Cache
                    if (!db.objectStoreNames.contains('seismic_cache')) {
                        db.createObjectStore('seismic_cache', { keyPath: 'id' });
                    }

                    // 4. Active Alerts
                    let alertStore;
                    if (!db.objectStoreNames.contains('active_alerts')) {
                        alertStore = db.createObjectStore('active_alerts', { keyPath: 'alert_id' });
                    } else {
                        alertStore = event.target.transaction.objectStore('active_alerts');
                    }
                    if (alertStore && !alertStore.indexNames.contains('expiry')) {
                        alertStore.createIndex('expiry', 'expiry', { unique: false });
                    }

                    // 5. Map Packages
                    if (!db.objectStoreNames.contains('map_packages')) {
                        db.createObjectStore('map_packages', { keyPath: 'package_id' });
                    }

                    // 6. Field Reports Sync Queue
                    if (!db.objectStoreNames.contains('sync_queue')) {
                        const queueStore = db.createObjectStore('sync_queue', { keyPath: 'local_id' });
                        queueStore.createIndex('sync_status', 'sync_status', { unique: false });
                        queueStore.createIndex('created_at', 'created_at', { unique: false });
                    }

                    // 7. User Preferences
                    if (!db.objectStoreNames.contains('user_preferences')) {
                        db.createObjectStore('user_preferences', { keyPath: 'key' });
                    }
                };

                request.onsuccess = (event) => {
                    this.db = event.target.result;
                    console.log('[LocalStore] IndexedDB v' + DB_VERSION + ' initialized successfully.');
                    resolve(this.db);
                };

                request.onerror = (event) => {
                    console.error('[LocalStore] Failed to open IndexedDB:', event.target.error);
                    resolve(null);
                };
            });
        }

        async _execute(storeName, mode, callback) {
            await this.readyPromise;
            if (!this.db) return null;

            return new Promise((resolve, reject) => {
                try {
                    const tx = this.db.transaction(storeName, mode);
                    const store = tx.objectStore(storeName);
                    const req = callback(store);

                    req.onsuccess = () => resolve(req.result);
                    req.onerror = () => reject(req.error);
                } catch (err) {
                    reject(err);
                }
            });
        }

        // =========================================================================
        // 1. PAHAD SNAPSHOTS (Canonical Phase 5B/5C Schema)
        // =========================================================================
        async saveSnapshot(snapshot) {
            if (!snapshot || !snapshot.sector_id) return null;
            const nowIso = new Date().toISOString();
            const record = {
                sector_id: snapshot.sector_id,
                timestamp: snapshot.timestamp || snapshot.timestamp_utc || nowIso,
                CRI: snapshot.CRI !== undefined ? snapshot.CRI : (snapshot.cri !== undefined ? snapshot.cri : 30.0),
                risk_band: snapshot.risk_band || 'LOW',
                FoS: snapshot.FoS !== undefined ? snapshot.FoS : (snapshot.fos_physical !== undefined ? snapshot.fos_physical : 1.5),
                event_probability: snapshot.event_probability !== undefined ? snapshot.event_probability : (snapshot.probability || 0.1),
                confidence: snapshot.confidence || 'HIGH_CONFIDENCE',
                model_version: snapshot.model_version || 'v5.2.0-phase5b',
                data_quality: snapshot.data_quality !== undefined ? snapshot.data_quality : (snapshot.data_quality_score || 1.0),
                source_status: snapshot.source_status || '[CACHED]',
                provenance: '[CACHED]',
                saved_at: nowIso,
                raw_payload: snapshot
            };
            return this._execute('pahad_snapshots', 'readwrite', (s) => s.put(record));
        }

        async getSnapshot(sectorId) {
            return this._execute('pahad_snapshots', 'readonly', (s) => s.get(sectorId));
        }

        async getAllSnapshots() {
            return this._execute('pahad_snapshots', 'readonly', (s) => s.getAll());
        }

        // =========================================================================
        // 2. ALERTS WITH AUTOMATIC EXPIRY RECONCILIATION
        // =========================================================================
        async saveAlert(alert) {
            if (!alert || !alert.alert_id) return null;
            const record = {
                alert_id: alert.alert_id,
                severity: alert.severity || 'INFO',
                issued_at: alert.issued_at || new Date().toISOString(),
                area: alert.area || 'NER Operational Sector',
                instruction: alert.instruction || '',
                status: alert.status || 'ACTIVE',
                expiry: alert.expiry || alert.expires_at || null,
                saved_at: new Date().toISOString()
            };
            return this._execute('active_alerts', 'readwrite', (s) => s.put(record));
        }

        async saveAlerts(alertsList) {
            if (!Array.isArray(alertsList)) return;
            for (const a of alertsList) {
                await this.saveAlert(a);
            }
        }

        async getActiveAlerts() {
            const all = await this._execute('active_alerts', 'readonly', (s) => s.getAll());
            if (!all) return [];

            const now = new Date();
            return all.map(a => {
                const isExpired = a.expiry && (new Date(a.expiry) <= now);
                return {
                    ...a,
                    is_expired: isExpired,
                    display_status: isExpired ? 'EXPIRED' : a.status
                };
            }).filter(a => !a.is_expired); // Only return unexpired alerts as active
        }

        async getAllAlerts() {
            const all = await this._execute('active_alerts', 'readonly', (s) => s.getAll());
            if (!all) return [];
            const now = new Date();
            return all.map(a => ({
                ...a,
                is_expired: !!(a.expiry && new Date(a.expiry) <= now)
            }));
        }

        // =========================================================================
        // 3. WEATHER & SEISMIC CACHE
        // =========================================================================
        async saveWeather(weatherData) {
            const record = {
                id: 'latest',
                data: weatherData,
                saved_at: new Date().toISOString()
            };
            return this._execute('weather_cache', 'readwrite', (s) => s.put(record));
        }

        async getWeather() {
            const res = await this._execute('weather_cache', 'readonly', (s) => s.get('latest'));
            return res ? res.data : null;
        }

        async saveSeismic(seismicData) {
            const record = {
                id: 'latest',
                data: seismicData,
                saved_at: new Date().toISOString()
            };
            return this._execute('seismic_cache', 'readwrite', (s) => s.put(record));
        }

        async getSeismic() {
            const res = await this._execute('seismic_cache', 'readonly', (s) => s.get('latest'));
            return res ? res.data : null;
        }

        // =========================================================================
        // 4. MAP PACKAGES
        // =========================================================================
        async saveMapPackage(pkg) {
            if (!pkg || !pkg.package_id) return null;
            const record = {
                ...pkg,
                saved_at: new Date().toISOString()
            };
            return this._execute('map_packages', 'readwrite', (s) => s.put(record));
        }

        async getMapPackage(packageId) {
            return this._execute('map_packages', 'readonly', (s) => s.get(packageId));
        }

        // =========================================================================
        // 5. SYNC QUEUE FOR OFFLINE FIELD REPORTS
        // =========================================================================
        async enqueueReport(reportPayload) {
            const localId = reportPayload.local_id || 'PN-OFFLINE-' + Date.now() + '-' + Math.random().toString(36).substr(2, 6);
            const record = {
                local_id: localId,
                server_id: null,
                report_data: reportPayload,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
                sync_status: 'QUEUED',
                retry_count: 0,
                error_message: null
            };
            await this._execute('sync_queue', 'readwrite', (s) => s.put(record));
            return record;
        }

        async getPendingReports() {
            await this.readyPromise;
            if (!this.db) return [];

            return new Promise((resolve, reject) => {
                const tx = this.db.transaction('sync_queue', 'readonly');
                const store = tx.objectStore('sync_queue');
                const index = store.index('sync_status');

                let results = [];
                const req1 = index.getAll('QUEUED');
                const req2 = index.getAll('PENDING_SYNC');
                const req3 = index.getAll('FAILED');

                req1.onsuccess = () => {
                    results = results.concat(req1.result || []);
                    req2.onsuccess = () => {
                        results = results.concat(req2.result || []);
                        req3.onsuccess = () => {
                            results = results.concat(req3.result || []);
                            resolve(results);
                        };
                    };
                };
                tx.onerror = () => reject(tx.error);
            });
        }

        async updateReportStatus(localId, newStatus, serverId = null, errorMessage = null) {
            const record = await this._execute('sync_queue', 'readonly', (s) => s.get(localId));
            if (!record) return null;

            record.sync_status = newStatus;
            record.updated_at = new Date().toISOString();
            if (serverId) record.server_id = serverId;
            if (errorMessage) {
                record.error_message = errorMessage;
                record.retry_count = (record.retry_count || 0) + 1;
            }

            return this._execute('sync_queue', 'readwrite', (s) => s.put(record));
        }

        async getAllQueueReports() {
            return this._execute('sync_queue', 'readonly', (s) => s.getAll());
        }
    }

    // Export globally
    window.ParvatLocalStore = new LocalDataStore();

})(window);

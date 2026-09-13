/**
 * PARVAT NETRA — Client-side Synchronization Engine (sync_manager.js)
 * Version: 3.2.0
 * 
 * Capabilities:
 * - Offline queue management in IndexedDB
 * - Idempotent deduplication using deterministic client local_id
 * - Reconnection auto-sync with exponential backoff
 * - Formal upload acknowledgements and state updates (PENDING_SYNC -> SYNCING -> SYNCED)
 */

(function(window) {
    'use strict';

    class SyncManager {
        constructor() {
            this.isSyncing = false;
            this.retryAttempt = 0;
            this.maxRetries = 5;
            this.baseDelayMs = 2000;
            this.retryTimeoutId = null;

            this._init();
        }

        _init() {
            // Listen for network state transitions to trigger automatic reconciliation
            window.addEventListener('parvat:network-change', (e) => {
                if (e.detail && e.detail.state === 'ONLINE') {
                    console.log('[SyncManager] Network restored to ONLINE. Triggering reconciliation queue...');
                    this.triggerSync();
                }
            });

            // Also check queue on page load after a brief delay
            setTimeout(() => {
                if (window.ParvatNetworkState && window.ParvatNetworkState.isOnline()) {
                    this.triggerSync();
                }
            }, 3000);
        }

        /**
         * Enqueues or submits an observational field report.
         * If online, tries immediate dispatch; on failure or offline, saves locally with PENDING_SYNC.
         */
        async submitFieldReport(reportData) {
            const localId = 'PN-OFFLINE-' + Date.now() + '-' + Math.random().toString(36).substr(2, 6);
            const payload = {
                ...reportData,
                local_id: localId,
                created_at: reportData.timestamp || new Date().toISOString()
            };

            // 1. Enqueue in IndexedDB
            let queuedRecord = null;
            if (window.ParvatLocalStore) {
                queuedRecord = await window.ParvatLocalStore.enqueueReport(payload);
            }

            // 2. If online, attempt immediate sync
            if (window.ParvatNetworkState && window.ParvatNetworkState.isOnline()) {
                try {
                    await this.syncSingleReport(payload);
                } catch (err) {
                    console.warn('[SyncManager] Immediate upload failed. Retaining in offline queue for retry:', err);
                }
            } else {
                console.log(`[SyncManager] Device offline. Stored report ${localId} in local IndexedDB queue.`);
            }

            return {
                local_id: localId,
                sync_status: queuedRecord ? queuedRecord.sync_status : 'PENDING_SYNC',
                queued_at: payload.created_at
            };
        }

        /**
         * Reconciles all pending and retry-pending reports with the server.
         */
        async triggerSync() {
            if (this.isSyncing) return;
            if (!window.ParvatLocalStore) return;

            const pending = await window.ParvatLocalStore.getPendingReports();
            if (!pending || pending.length === 0) {
                return;
            }

            console.log(`[SyncManager] Starting sync of ${pending.length} pending reports...`);
            this.isSyncing = true;
            if (window.ParvatNetworkState) {
                window.ParvatNetworkState.setState('SYNCING', { pendingCount: pending.length });
            }

            const batchPayload = pending.map((item) => ({
                local_id: item.local_id,
                ...item.report_data
            }));

            try {
                const response = await fetch('/api/sync/field-reports', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ reports: batchPayload })
                });

                if (!response.ok) {
                    throw new Error(`Server returned HTTP ${response.status}`);
                }

                const result = await response.json();
                const acks = result.acknowledgements || [];

                for (const ack of acks) {
                    if (ack.sync_status === 'SYNCED') {
                        await window.ParvatLocalStore.updateReportStatus(
                            ack.local_id,
                            'SYNCED',
                            ack.server_id
                        );
                        console.log(`[SyncManager] Report ${ack.local_id} -> SYNCED (Server ID: ${ack.server_id})`);
                    } else {
                        await window.ParvatLocalStore.updateReportStatus(
                            ack.local_id,
                            'RETRY_PENDING',
                            null,
                            ack.error
                        );
                    }
                }

                this.retryAttempt = 0;
                if (window.ParvatNetworkState) {
                    window.ParvatNetworkState.setState('ONLINE', { syncedCount: result.synced_count });
                }
            } catch (err) {
                console.error('[SyncManager] Sync failed:', err);
                this._scheduleRetry(pending);
                if (window.ParvatNetworkState) {
                    window.ParvatNetworkState.setState('DEGRADED', { syncError: err.message });
                }
            } finally {
                this.isSyncing = false;
            }
        }

        async syncSingleReport(payload) {
            const response = await fetch('/api/sync/field-reports', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ reports: [payload] })
            });

            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            const ack = (data.acknowledgements || [])[0];

            if (ack && ack.sync_status === 'SYNCED' && window.ParvatLocalStore) {
                await window.ParvatLocalStore.updateReportStatus(payload.local_id, 'SYNCED', ack.server_id);
            }
            return ack;
        }

        _scheduleRetry(pendingItems) {
            if (this.retryAttempt >= this.maxRetries) {
                console.warn('[SyncManager] Max retry attempts reached. Will wait for next online event.');
                return;
            }

            this.retryAttempt++;
            const delay = this.baseDelayMs * Math.pow(2, this.retryAttempt - 1);
            console.log(`[SyncManager] Scheduling retry ${this.retryAttempt}/${this.maxRetries} in ${delay}ms...`);

            if (this.retryTimeoutId) clearTimeout(this.retryTimeoutId);
            this.retryTimeoutId = setTimeout(() => {
                this.triggerSync();
            }, delay);
        }

        async getQueueMetrics() {
            if (!window.ParvatLocalStore) return { total: 0, pending: 0, synced: 0 };
            const all = await window.ParvatLocalStore.getAllQueueReports();
            const pending = all.filter(r => r.sync_status === 'PENDING_SYNC' || r.sync_status === 'RETRY_PENDING').length;
            const synced = all.filter(r => r.sync_status === 'SYNCED').length;
            return {
                total: all.length,
                pending: pending,
                synced: synced
            };
        }
    }

    // Export globally
    window.ParvatSyncManager = new SyncManager();

})(window);

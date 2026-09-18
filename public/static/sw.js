/**
 * PARVAT NETRA — Service Worker (PWA & Offline Resilience Engine)
 * Version: 3.2.0
 * 
 * Strict Cache Policies:
 * - CACHE-FIRST: App shell, static CSS, JS, images, pre-bundled offline map package
 * - STALE-WHILE-REVALIDATE: Non-critical historical GIS metadata & offline manifest
 * - NETWORK-FIRST WITH CACHE FALLBACK: Live PAHAD predictions, weather, seismic, active alerts
 * 
 * Safety Rules:
 * - NEVER cache passwords, auth tokens, login cookies, or arbitrary POST requests
 * - Never intercept requests in a way that breaks authentication
 */

const CACHE_NAME = 'parvat-netra-v5.5.0';
const DYNAMIC_CACHE_NAME = 'parvat-netra-dynamic-v5.5.0';

const PRECACHE_ASSETS = [
    '/',
    '/static/manifest.json',
    '/static/images/parvat_netra_emblem.png',
    '/static/css/parvat_theme.css',
    '/static/js/i18n.js',
    '/static/js/network_state.js',
    '/static/js/local_store.js',
    '/static/js/sync_manager.js',
    '/static/js/offline_manager.js',
    '/static/js/offline_routing.js',
    '/static/js/winning_modals.js',
    '/static/pahad_offline_cache.json',
    '/static/data/offline_core_package.json',
    '/api/geospatial/offline-manifest',
    '/api/pahad/event-model/status',
    '/api/pahad/event-model/data-quality',
    '/api/hardware/bom',
    '/api/sitrep/official-memo?scenario=glof',
    '/api/sitrep/official-memo?scenario=remal',
    '/api/sitrep/official-memo?scenario=tupul',
    '/api/sitrep/official-memo?scenario=sonapur',
    '/edge-network',
    '/demo',
    '/static/js/offline_field_triage.js'
];

// URLs that must NEVER be cached (Auth, Passwords, Session Management, Push Sync)
const EXCLUDED_URL_PATTERNS = [
    /\/login/i,
    /\/logout/i,
    /\/auth/i,
    /\/api\/decisions\/.*\/authorize/i,
    /\/api\/alerts\/dispatch-siren/i,
    /\/api\/sync\/push/i,
    /\/api\/sync\/field-reports/i
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('[SW] Pre-caching core operational app shell & offline vector package');
            return cache.addAll(PRECACHE_ASSETS).catch((err) => {
                console.warn('[SW] Some precache assets failed to load during install:', err);
            });
        }).then(() => self.skipWaiting())
    );
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((name) => {
                    if (name !== CACHE_NAME && name !== DYNAMIC_CACHE_NAME) {
                        console.log('[SW] Pruning legacy cache:', name);
                        return caches.delete(name);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', (event) => {
    const request = event.request;
    const url = new URL(request.url);

    // Rule 1: Only handle GET requests. POST/PUT/DELETE must pass directly through to network.
    if (request.method !== 'GET') {
        return;
    }

    // Rule 2: Security exclusion for auth and secret management
    for (const pattern of EXCLUDED_URL_PATTERNS) {
        if (pattern.test(url.pathname)) {
            return; // Pass through without SW caching
        }
    }

    // Rule 3: CACHE-FIRST for Static Assets & Offline Map Packages
    if (url.pathname.startsWith('/static/') || url.pathname === '/favicon.ico') {
        event.respondWith(
            caches.match(request).then((cachedResponse) => {
                if (cachedResponse) {
                    return cachedResponse;
                }
                return fetch(request).then((networkResponse) => {
                    if (networkResponse && networkResponse.status === 200) {
                        const responseClone = networkResponse.clone();
                        caches.open(CACHE_NAME).then((cache) => cache.put(request, responseClone));
                    }
                    return networkResponse;
                });
            })
        );
        return;
    }

    // Rule 4: STALE-WHILE-REVALIDATE for Geospatial Metadata & Historical Datasets
    if (url.pathname.startsWith('/api/geospatial/')) {
        event.respondWith(
            caches.open(DYNAMIC_CACHE_NAME).then((cache) => {
                return cache.match(request).then((cachedResponse) => {
                    const fetchPromise = fetch(request).then((networkResponse) => {
                        if (networkResponse && networkResponse.status === 200) {
                            cache.put(request, networkResponse.clone());
                        }
                        return networkResponse;
                    }).catch(() => cachedResponse);

                    return cachedResponse || fetchPromise;
                });
            })
        );
        return;
    }

    // Rule 5: NETWORK-FIRST WITH CACHE FALLBACK for Live Predictions, Telemetry, Weather, Seismic & Sync Pull
    if (
        url.pathname.startsWith('/api/pahad/') ||
        url.pathname.startsWith('/api/weather/') ||
        url.pathname.startsWith('/api/seismic/') ||
        url.pathname.startsWith('/api/alerts/') ||
        url.pathname.startsWith('/api/ml/') ||
        url.pathname.startsWith('/api/spatial/') ||
        url.pathname.startsWith('/api/kpis') ||
        url.pathname.startsWith('/api/sync/pull') ||
        url.pathname.startsWith('/api/sync/status') ||
        url.pathname.startsWith('/api/routing/') ||
        url.pathname.startsWith('/api/shelters')
    ) {
        event.respondWith(
            fetch(request)
                .then((networkResponse) => {
                    if (networkResponse && networkResponse.status === 200) {
                        const responseClone = networkResponse.clone();
                        caches.open(DYNAMIC_CACHE_NAME).then((cache) => cache.put(request, responseClone));
                    }
                    return networkResponse;
                })
                .catch(() => {
                    // Network failed — fallback to most recent valid cached snapshot
                    return caches.match(request).then((cachedResponse) => {
                        if (cachedResponse) {
                            // Inject header to notify client of cached provenance
                            const headers = new Headers(cachedResponse.headers);
                            headers.set('X-Parvat-Cached', 'true');
                            headers.set('X-Parvat-Provenance', '[CACHED]');
                            return cachedResponse.blob().then((blob) => {
                                return new Response(blob, {
                                    status: 200,
                                    statusText: 'OK (Cached Offline Fallback)',
                                    headers: headers
                                });
                            });
                        }
                        // If completely un-cached, return structured JSON error
                        return new Response(JSON.stringify({
                            status: "DEGRADED",
                            offline: true,
                            provenance: "[CACHED]",
                            message: "Live telemetry offline; cached snapshot not yet archived."
                        }), {
                            status: 200,
                            headers: { 'Content-Type': 'application/json' }
                        });
                    });
                })
        );
        return;
    }

    // Rule 6: Navigation Requests (HTML Pages: /, /climate-map, /seismic, /terrain-3d)
    if (request.mode === 'navigate') {
        event.respondWith(
            fetch(request).catch(() => {
                return caches.match(request).then((cachedPage) => {
                    if (cachedPage) {
                        return cachedPage;
                    }
                    return caches.match('/');
                });
            })
        );
        return;
    }

    // Default: Network with Cache Fallback
    event.respondWith(
        fetch(request).catch(() => caches.match(request))
    );
});

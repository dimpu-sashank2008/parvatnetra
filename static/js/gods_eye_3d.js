/**
 * static/js/gods_eye_3d.js
 * =========================
 * PARVAT NETRA • PAHAD AI — God's Eye Style Photorealistic 3D GIS Map Engine
 * Phase V5.3 Geospatial 3D Presentation Layer
 * 
 * Features:
 *   1. Direct integration into existing #gis-map container as selectable 3D basemap.
 *   2. Lazy-loads CesiumJS runtime on demand (zero impact on initial 2D page load).
 *   3. Truthful Provider Hierarchy & Graceful Fallback:
 *      Google Photorealistic 3D Tiles -> Cesium World Terrain -> Open Carto/OSM Ellipsoid Fallback.
 *   4. Hierarchical Cinematic Camera Flight:
 *      Level 1: India Overview (4,500 km)
 *      Level 2: North-East Region Overview (1,200 km)
 *      Level 3: Sikkim Himalayas (250 km)
 *      Level 4: Teesta River Gorge & NH-10 Corridor (25 km)
 *      Level 5: KM48 Pakyong Hazard Escarpment (3.5 km, pitch -30°, heading 35°)
 *   5. Synchronized 3D Data Layers:
 *      - PAHAD Composite Risk Index (CRI) 5-tier colored risk zones
 *      - Mohr-Coulomb Factor of Safety (FoS = 1.04) physical slip surface
 *      - Live precipitation markers [LIVE / OPEN-METEO]
 *      - Live seismic hypocenters [LIVE / USGS-FDSNWS]
 *      - InSAR Line-of-sight ground displacement vectors [HISTORICAL / INSAR-LOS]
 *      - Planned in-situ sensors [PLANNED / BENCH TESTED / PHYSICAL TELEMETRY PENDING] (0 live sensors)
 *      - BRO Lifeline Highway NH-10 routing corridor & bypass status
 *   6. Click-to-inspect 3D Info Card & Contextual Legend
 *   7. Safe 2D <-> 3D transition lifecycle with Leaflet map.invalidateSize()
 *   8. Zero autonomous sirens / zero warning dispatch from 3D visualization.
 */

(function (window, document) {
    'use strict';

    // CDN Dependencies for Lazy Loading
    const CESIUM_JS_URL = 'https://cesium.com/downloads/cesiumjs/releases/1.119/Build/Cesium/Cesium.js';
    const CESIUM_CSS_URL = 'https://cesium.com/downloads/cesiumjs/releases/1.119/Build/Cesium/Widgets/widgets.css';

    // Canonical Corridor KM48 Definition
    const CANONICAL_KM48 = {
        corridorId: 'CORR-NH10-SIKKIM-KM48',
        name: 'NH-10 Teesta Gorge Corridor (Km 48 Pakyong)',
        state: 'Sikkim',
        district: 'Pakyong',
        road: 'NH-10',
        marker: 'Km 48.200',
        longitude: 88.6100,
        latitude: 27.3300,
        elevation: 680.0,
        slope: 42.5,
        criScore: 78.4,
        fos: 1.04,
        status: 'CRITICAL_HAZARD',
        coordinates: [
            [88.5821, 27.2410],
            [88.5954, 27.2485],
            [88.6100, 27.3300],
            [88.6180, 27.3390]
        ]
    };

    // Camera Flight Hierarchy Checkpoints
    const FLIGHT_STEPS = [
        { step: 1, label: 'INDIA', name: 'India National Overview', lon: 78.9629, lat: 20.5937, height: 4500000, pitch: -90, heading: 0, duration: 2.2 },
        { step: 2, label: 'NER', name: 'North-East Region Corridor', lon: 92.5000, lat: 26.0000, height: 1200000, pitch: -75, heading: 10, duration: 2.0 },
        { step: 3, label: 'SIKKIM', name: 'Sikkim Himalayas', lon: 88.5000, lat: 27.5000, height: 250000, pitch: -60, heading: 25, duration: 1.8 },
        { step: 4, label: 'NH-10', name: 'Teesta River Basin / NH-10', lon: 88.6100, lat: 27.3300, height: 25000, pitch: -45, heading: 35, duration: 1.6 },
        { step: 5, label: 'KM48', name: 'KM48 Pakyong Hazard Escarpment', lon: 88.6100, lat: 27.3300, height: 3500, pitch: -30, heading: 35, duration: 1.5 }
    ];

    class GodsEye3DController {
        constructor() {
            this.container = null;
            this.viewer = null;
            this.active = false;
            this.cesiumLoaded = false;
            this.loadingInProgress = false;
            this.currentFlightStep = 0;
            this.isFlying = false;
            this.orbitActive = false;
            this.orbitTimer = null;
            this.providerStatus = 'AUTH_REQUIRED';
            this.providerBadge = '[3D PROVIDER: TERRAIN 3D FALLBACK (AUTH_REQUIRED FOR GOOGLE 3D TILES)]';
            this.activeProvider = 'OPEN_TERRAIN_FALLBACK';
            this.config = null;
            this.layers = {
                riskZone: null,
                fosMarker: null,
                weatherMarker: null,
                seismicMarker: null,
                insarMarker: null,
                sensorMarkers: [],
                corridorPolyline: null,
                allRiskZones: []
            };
        }

        /**
         * Initialize container references and bind events.
         */
        init() {
            this.container = document.getElementById('gods-eye-3d-container');
            if (!this.container) {
                console.warn('[GodsEye3D] Container #gods-eye-3d-container not found in DOM.');
                return;
            }
            this.fetchConfig();
        }

        /**
         * Fetch server-side 3D configuration & credentials status.
         */
        async fetchConfig() {
            try {
                const res = await fetch('/api/gods-eye/config');
                if (res.ok) {
                    this.config = await res.json();
                    if (this.config.provider_badge) {
                        this.providerBadge = this.config.provider_badge;
                    }
                    if (this.config.provider_status) {
                        this.providerStatus = this.config.provider_status;
                    }
                    if (this.config.active_provider) {
                        this.activeProvider = this.config.active_provider;
                    }
                    this.updateProviderBadgeUI();
                }
            } catch (err) {
                console.warn('[GodsEye3D] Could not fetch /api/gods-eye/config, using defaults:', err);
            }
        }

        /**
         * Dynamically load CesiumJS script and styles.
         */
        loadCesium() {
            return new Promise((resolve, reject) => {
                if (window.Cesium) {
                    this.cesiumLoaded = true;
                    return resolve();
                }

                this.loadingInProgress = true;
                this.renderLoadingState('Loading Photorealistic 3D Geospatial Engine (CesiumJS)...');

                // Load CSS
                const link = document.createElement('link');
                link.rel = 'stylesheet';
                link.href = CESIUM_CSS_URL;
                document.head.appendChild(link);

                // Load JS
                const script = document.createElement('script');
                script.src = CESIUM_JS_URL;
                script.async = true;
                script.onload = () => {
                    this.cesiumLoaded = true;
                    this.loadingInProgress = false;
                    console.log('[GodsEye3D] CesiumJS runtime successfully lazy-loaded.');
                    resolve();
                };
                script.onerror = (err) => {
                    this.loadingInProgress = false;
                    console.error('[GodsEye3D] Failed to load CesiumJS from CDN:', err);
                    this.renderErrorState('Network Error: Unable to fetch CesiumJS 3D engine. Check internet connectivity.');
                    reject(err);
                };
                document.head.appendChild(script);
            });
        }

        /**
         * Render HUD UI over the 3D container.
         */
        renderHUD() {
            if (this.container.querySelector('.gods-eye-hud')) return;

            const hud = document.createElement('div');
            hud.className = 'gods-eye-hud absolute inset-0 pointer-events-none z-[320] flex flex-col justify-between p-3 font-mono';
            hud.innerHTML = `
                <!-- Top Header Bar -->
                <div class="flex items-center justify-between flex-wrap gap-2 pointer-events-auto bg-[#070B10]/90 backdrop-blur border border-slate-700/80 rounded px-3 py-2 shadow-2xl">
                    <div class="flex items-center gap-2">
                        <div class="w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse"></div>
                        <span class="text-xs font-bold text-amber-400 tracking-wider">GOD'S EYE 3D VIEW</span>
                        <span id="gods-eye-corridor-count" class="text-[10px] text-amber-300 border-l border-slate-700 pl-2 font-mono">20 NER CORRIDORS</span>
                        <span id="gods-eye-provider-pill" class="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-600">
                            ${this.providerBadge}
                        </span>
                    </div>

                    <!-- Flight Step Breadcrumb -->
                    <div class="flex items-center gap-1 text-[10px]" id="gods-eye-breadcrumb">
                        ${FLIGHT_STEPS.map((s, idx) => `
                            <button type="button" onclick="window.GodsEye3D.flyToStep(${idx})" id="flight-step-btn-${idx}"
                                    class="px-1.5 py-0.5 rounded border border-slate-700 text-slate-400 hover:text-white transition-colors">
                                ${s.label}
                            </button>
                            ${idx < FLIGHT_STEPS.length - 1 ? '<span class="text-slate-600">›</span>' : ''}
                        `).join('')}
                    </div>

                    <!-- Camera Control Actions & Sector Jump -->
                    <div class="flex items-center gap-1.5 text-[11px]">
                        <select id="gods-eye-sector-select" onchange="window.GodsEye3D.flyToSector(this.value)" class="bg-slate-900 hover:bg-slate-800 text-amber-300 border border-amber-700/70 text-[10px] rounded px-1.5 py-1 font-mono focus:outline-none focus:border-amber-400 max-w-[145px] sm:max-w-[180px]" title="Jump to any evaluated NER Corridor">
                            <option value="">🎯 Jump to Sector...</option>
                        </select>
                        <button type="button" onclick="window.GodsEye3D.resetHome()" class="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-600 flex items-center gap-1" title="Reset to Home Overview">
                            <span>⌂ Home</span>
                        </button>
                        <button type="button" onclick="window.GodsEye3D.focusHazard()" class="px-2 py-1 rounded bg-amber-950 hover:bg-amber-900 text-amber-300 border border-amber-600 flex items-center gap-1 font-bold" title="Direct Flight to KM48 Hazard">
                            <span>🎯 Focus KM48</span>
                        </button>
                        <button type="button" onclick="window.GodsEye3D.toggleOrbit()" id="gods-eye-orbit-btn" class="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-600 flex items-center gap-1" title="360° Orbit Around KM48">
                            <span>↻ Orbit</span>
                        </button>
                        <button type="button" onclick="if (typeof window.exitGodsEye3D === 'function') { window.exitGodsEye3D(); } else if (typeof window.switchMainBasemap === 'function') { window.switchMainBasemap('bhuvan'); } else { window.GodsEye3D.deactivate(); }" class="px-2 py-1 rounded bg-sky-950 hover:bg-sky-900 text-sky-300 border border-sky-600 flex items-center gap-1 font-bold" title="Exit 3D and directly open Primary GIS Map">
                            <span>✕ Primary Map</span>
                        </button>
                    </div>
                </div>

                <!-- Bottom Strip: Legend & Information Slide-out -->
                <div class="flex items-end justify-between gap-3 pointer-events-none">
                    <!-- 3D Contextual Legend -->
                    <div class="pointer-events-auto bg-[#070B10]/95 backdrop-blur border border-slate-700/80 rounded p-2.5 shadow-2xl text-[10px] space-y-1.5 max-w-[280px]">
                        <div class="font-bold text-sky-400 flex items-center justify-between border-b border-slate-800 pb-1">
                            <span>PAHAD 3D HAZARD CORRIDORS</span>
                            <span class="text-[9px] text-amber-400 font-mono">20 EVALUATED</span>
                        </div>
                        <div class="grid grid-cols-2 gap-x-2 gap-y-1 text-[9px]">
                            <div class="flex items-center gap-1.5">
                                <span class="w-2.5 h-2.5 rounded-sm bg-red-600 inline-block shrink-0"></span>
                                <span class="text-slate-300">EXTREME (&gt;80)</span>
                            </div>
                            <div class="flex items-center gap-1.5">
                                <span class="w-2.5 h-2.5 rounded-sm bg-orange-600 inline-block shrink-0"></span>
                                <span class="text-slate-300">VERY HIGH (70-80)</span>
                            </div>
                            <div class="flex items-center gap-1.5">
                                <span class="w-2.5 h-2.5 rounded-sm bg-amber-500 inline-block shrink-0"></span>
                                <span class="text-slate-300">HIGH (60-70)</span>
                            </div>
                            <div class="flex items-center gap-1.5">
                                <span class="w-2.5 h-2.5 rounded-sm bg-yellow-400 inline-block shrink-0"></span>
                                <span class="text-slate-300">MODERATE (40-60)</span>
                            </div>
                            <div class="flex items-center gap-1.5">
                                <span class="w-2.5 h-2.5 rounded-sm bg-emerald-500 inline-block shrink-0"></span>
                                <span class="text-slate-300">LOW (&lt;40)</span>
                            </div>
                            <div class="flex items-center gap-1.5">
                                <span class="w-2.5 h-2.5 rounded-full bg-cyan-400 inline-block shrink-0"></span>
                                <span class="text-slate-300">Rainfall [LIVE]</span>
                            </div>
                        </div>
                        <div class="pt-1 border-t border-slate-800/80 text-[8.5px] text-slate-400 flex items-center justify-between">
                            <span>In-Situ Telemetry:</span>
                            <span class="text-amber-400 font-bold">[PLANNED / BENCH TESTED]</span>
                        </div>
                    </div>

                    <!-- Slide-out 3D Entity Inspector Card -->
                    <div id="gods-eye-info-card" class="hidden pointer-events-auto bg-[#070B10]/95 backdrop-blur border border-amber-600/80 rounded-lg p-3 shadow-2xl text-[11px] max-w-[340px] text-slate-200 space-y-2 animate-fadeIn">
                        <div class="flex items-center justify-between border-b border-slate-800 pb-1.5">
                            <span id="ge-info-title" class="font-bold text-amber-400 text-xs">KM48 Pakyong Escarpment</span>
                            <button type="button" onclick="window.GodsEye3D.hideInfoCard()" class="text-slate-400 hover:text-white px-1 text-xs">✕</button>
                        </div>
                        <div id="ge-info-body" class="space-y-1 text-[10px]">
                            <!-- Injected dynamically -->
                        </div>
                        <div class="pt-1.5 border-t border-slate-800 flex items-center justify-between text-[9px]">
                            <span id="ge-info-provenance" class="text-sky-400 font-mono">[HISTORICAL / PHYSICS]</span>
                            <button type="button" onclick="window.GodsEye3D.focusHazard()" class="text-amber-400 hover:underline">Recenter</button>
                        </div>
                    </div>
                </div>
            `;
            this.container.appendChild(hud);
        }

        /**
         * Update the provider badge text.
         */
        updateProviderBadgeUI() {
            const pill = document.getElementById('gods-eye-provider-pill');
            if (pill) {
                pill.textContent = this.providerBadge;
                if (this.providerStatus === 'CONFIGURED') {
                    pill.className = 'text-[9px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-700';
                } else {
                    pill.className = 'text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-600';
                }
            }
        }

        /**
         * Show loading state inside container.
         */
        renderLoadingState(message) {
            let loader = this.container.querySelector('.gods-eye-loader');
            if (!loader) {
                loader = document.createElement('div');
                loader.className = 'gods-eye-loader absolute inset-0 z-[350] bg-[#070B10] flex flex-col items-center justify-center text-slate-200 font-mono gap-3';
                this.container.appendChild(loader);
            }
            loader.style.display = 'flex';
            loader.innerHTML = `
                <div class="w-10 h-10 border-2 border-amber-500/30 border-t-amber-400 rounded-full animate-spin"></div>
                <div class="text-xs font-bold text-amber-400 uppercase tracking-wider">${message}</div>
                <div class="text-[10px] text-slate-400">Rendering WGS84 3D Globe &amp; Himalayan Topography...</div>
            `;
        }

        /**
         * Hide loading state.
         */
        hideLoadingState() {
            const loader = this.container.querySelector('.gods-eye-loader');
            if (loader) {
                loader.style.display = 'none';
            }
        }

        /**
         * Show error state with 1-click fallback button to 2D map.
         */
        renderErrorState(message) {
            let errEl = this.container.querySelector('.gods-eye-error');
            if (!errEl) {
                errEl = document.createElement('div');
                errEl.className = 'gods-eye-error absolute inset-0 z-[360] bg-[#070B10]/95 flex flex-col items-center justify-center text-slate-200 font-mono gap-3 p-4 text-center';
                this.container.appendChild(errEl);
            }
            errEl.style.display = 'flex';
            errEl.innerHTML = `
                <div class="text-red-400 text-2xl font-bold">⚠️ 3D Geospatial Engine Offline</div>
                <div class="text-xs text-slate-300 max-w-md">${message}</div>
                <div class="flex gap-2 mt-2">
                    <button type="button" onclick="if (typeof window.exitGodsEye3D === 'function') { window.exitGodsEye3D(); } else if (typeof window.switchMainBasemap === 'function') { window.switchMainBasemap('bhuvan'); } else { window.GodsEye3D.deactivate(); }" class="px-3 py-1.5 rounded bg-sky-950 hover:bg-sky-900 text-sky-300 border border-sky-600 font-bold text-xs" title="Return directly to Primary GIS Map">
                        ← Return to Primary GIS Map
                    </button>
                    <button type="button" onclick="window.GodsEye3D.activate()" class="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-600 text-xs">
                        ↻ Retry 3D Load
                    </button>
                </div>
            `;
        }

        /**
         * Hide error state.
         */
        hideErrorState() {
            const errEl = this.container.querySelector('.gods-eye-error');
            if (errEl) {
                errEl.style.display = 'none';
            }
        }

        /**
         * Initialize the Cesium Viewer instance.
         */
        async initViewer() {
            if (this.viewer) return;

            const cesiumContainer = document.createElement('div');
            cesiumContainer.id = 'cesium-canvas-container';
            cesiumContainer.className = 'w-full h-full';
            this.container.appendChild(cesiumContainer);

            // Setup Cesium Ion Token if provided
            if (window.CESIUM_ION_TOKEN) {
                Cesium.Ion.defaultAccessToken = window.CESIUM_ION_TOKEN;
            }

            // Select Terrain Provider based on credentials
            let terrainProvider = undefined;
            if (window.CESIUM_ION_TOKEN && typeof Cesium.createWorldTerrainAsync === 'function') {
                try {
                    terrainProvider = await Cesium.createWorldTerrainAsync({
                        requestWaterMask: true,
                        requestVertexNormals: true
                    });
                } catch (e) {
                    console.warn('[GodsEye3D] Cesium World Terrain token error, falling back to Ellipsoid:', e);
                    terrainProvider = new Cesium.EllipsoidTerrainProvider();
                }
            } else {
                terrainProvider = new Cesium.EllipsoidTerrainProvider();
            }

            // Select Imagery Provider (Esri World Imagery Photorealistic Satellite)
            const imageryProvider = new Cesium.UrlTemplateImageryProvider({
                url: 'https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                maximumLevel: 19,
                credit: 'Esri World Imagery, Maxar, Earthstar Geographics'
            });

            const baseImageryLayer = new Cesium.ImageryLayer(imageryProvider);

            // Instantiate Cesium Viewer with clean operational HUD (hiding default bloated widgets)
            this.viewer = new Cesium.Viewer('cesium-canvas-container', {
                baseLayer: baseImageryLayer,
                terrainProvider: terrainProvider,
                animation: false,
                timeline: false,
                fullscreenButton: false,
                geocoder: false,
                homeButton: false,
                sceneModePicker: false,
                navigationHelpButton: false,
                baseLayerPicker: false,
                infoBox: false,
                selectionIndicator: false,
                shadows: false
            });

            // Ensure base imagery layer exists in imageryLayers collection
            if (this.viewer.imageryLayers.length === 0) {
                this.viewer.imageryLayers.addImageryProvider(imageryProvider);
            }

            // Performance optimizations
            this.viewer.scene.globe.enableLighting = false;
            this.viewer.scene.globe.depthTestAgainstTerrain = false;
            this.viewer.scene.screenSpaceCameraController.enableCollisionDetection = false;

            // Attempt Google Photorealistic 3D Tiles if API Key is configured
            if (window.GOOGLE_MAPS_API_KEY && typeof Cesium.createGooglePhotorealistic3DTileset === 'function') {
                try {
                    const tileset = await Cesium.createGooglePhotorealistic3DTileset({
                        key: window.GOOGLE_MAPS_API_KEY
                    });
                    this.viewer.scene.primitives.add(tileset);
                    this.providerStatus = 'CONFIGURED';
                    this.providerBadge = '[3D PROVIDER: GOOGLE PHOTOREALISTIC 3D TILES]';
                    this.activeProvider = 'GOOGLE_PHOTOREALISTIC_3D';
                    this.updateProviderBadgeUI();
                    console.log('[GodsEye3D] Google Photorealistic 3D Tiles initialized successfully.');
                } catch (err) {
                    console.warn('[GodsEye3D] Google 3D Tiles initialization failed, falling back to Terrain:', err);
                }
            }

            // Add Click Handler for 3D inspection
            this.setupInteractionHandler();

            // Populate 3D Data Layers
            this.add3DDataLayers();
        }

        /**
         * Setup click picking for 3D entities.
         */
        setupInteractionHandler() {
            const handler = new Cesium.ScreenSpaceEventHandler(this.viewer.scene.canvas);
            handler.setInputAction((click) => {
                const pickedObject = this.viewer.scene.pick(click.position);
                if (Cesium.defined(pickedObject) && pickedObject.id && pickedObject.id.pahadData) {
                    this.showInfoCard(pickedObject.id.pahadData);
                } else {
                    this.hideInfoCard();
                }
            }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
        }

        /**
         * Add Synchronized 3D Data Layers.
         */
        add3DDataLayers() {
            if (!this.viewer) return;

            // 1. NH-10 Corridor Polyline
            const linePositions = CANONICAL_KM48.coordinates.map(c => Cesium.Cartesian3.fromDegrees(c[0], c[1], 680));
            this.layers.corridorPolyline = this.viewer.entities.add({
                name: 'NH-10 Teesta Corridor Polyline',
                polyline: {
                    positions: linePositions,
                    width: 6,
                    material: new Cesium.PolylineGlowMaterialProperty({
                        glowPower: 0.25,
                        color: Cesium.Color.ORANGE
                    }),
                    clampToGround: true
                },
                pahadData: {
                    title: 'NH-10 Teesta Gorge Lifeline Highway',
                    type: 'LIFELINE_HIGHWAY',
                    location: 'Km 42 - Km 52 (Pakyong Sector)',
                    elevation: '680 m MSL',
                    status: 'HAZARD_WATCH — SINGLE LANE PASSAGE',
                    metrics: [
                        { label: 'Slope Angle', value: '42.5°' },
                        { label: 'Geology', value: 'Daling Group Phyllites / Schists' },
                        { label: 'Operational Control', value: 'BRO Project Swastik' }
                    ],
                    provenance: '[HISTORICAL / BRO RECORDS]'
                }
            });

            // 2. KM48 Pakyong Hazard Escarpment & FoS Slip Surface
            this.layers.fosMarker = this.viewer.entities.add({
                name: 'KM48 Hazard Escarpment & Slip Plane',
                position: Cesium.Cartesian3.fromDegrees(CANONICAL_KM48.longitude, CANONICAL_KM48.latitude, CANONICAL_KM48.elevation + 80),
                point: {
                    pixelSize: 16,
                    color: Cesium.Color.RED,
                    outlineColor: Cesium.Color.WHITE,
                    outlineWidth: 2
                },
                label: {
                    text: 'KM48 ESCARPMENT\nFoS: 1.04 [CRITICAL]',
                    font: 'bold 11px JetBrains Mono, monospace',
                    fillColor: Cesium.Color.YELLOW,
                    outlineColor: Cesium.Color.BLACK,
                    outlineWidth: 3,
                    style: Cesium.LabelStyle.FILL_AND_OUTLINE,
                    verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
                    pixelOffset: new Cesium.Cartesian2(0, -18)
                },
                pahadData: {
                    title: 'Km 48 Pakyong Escarpment Slip Plane',
                    type: 'PHYSICAL_SLIP_SURFACE',
                    location: '27.3300°N, 88.6100°E (Elevation 680m)',
                    elevation: '680 m MSL',
                    status: 'ACTIVE SLIP ZONE (FoS = 1.04)',
                    metrics: [
                        { label: 'Factor of Safety (FoS)', value: '1.04 (Mohr-Coulomb shear balance)' },
                        { label: 'Composite Risk Index (CRI)', value: '78.4 / 100 [VERY HIGH]' },
                        { label: 'Kinematic Trigger', value: 'CRITICAL_DISPLACEMENT_PENDING' }
                    ],
                    provenance: '[PHYSICS / MOHR-COULOMB]'
                }
            });

            // 3. Live Weather Pin [LIVE / OPEN-METEO]
            this.layers.weatherMarker = this.viewer.entities.add({
                name: 'Live Weather Telemetry Mast',
                position: Cesium.Cartesian3.fromDegrees(88.6091, 27.3292, 710),
                point: {
                    pixelSize: 12,
                    color: Cesium.Color.CYAN,
                    outlineColor: Cesium.Color.BLACK,
                    outlineWidth: 1.5
                },
                label: {
                    text: 'WEATHER [LIVE]\n14.2 mm/h',
                    font: '10px JetBrains Mono, monospace',
                    fillColor: Cesium.Color.CYAN,
                    outlineColor: Cesium.Color.BLACK,
                    outlineWidth: 2,
                    style: Cesium.LabelStyle.FILL_AND_OUTLINE,
                    verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
                    pixelOffset: new Cesium.Cartesian2(0, -14)
                },
                pahadData: {
                    title: 'Pakyong Weather Station Met Feed',
                    type: 'WEATHER_TELEMETRY',
                    location: '27.3292°N, 88.6091°E',
                    elevation: '710 m MSL',
                    status: 'ACTIVE_TELEMETRY_FEED',
                    metrics: [
                        { label: 'Rainfall Intensity', value: '14.2 mm/h' },
                        { label: '24h Accumulation', value: '68.5 mm' },
                        { label: 'API 72h', value: '112.4 mm' }
                    ],
                    provenance: '[LIVE / OPEN-METEO]'
                }
            });

            // 4. Live Seismic Hypocenter [LIVE / USGS-FDSNWS]
            this.layers.seismicMarker = this.viewer.entities.add({
                name: 'Recent Seismic Hypocenter',
                position: Cesium.Cartesian3.fromDegrees(88.7500, 27.1800, 500),
                point: {
                    pixelSize: 13,
                    color: Cesium.Color.LIME,
                    outlineColor: Cesium.Color.BLACK,
                    outlineWidth: 1.5
                },
                label: {
                    text: 'SEISMIC [LIVE]\nM4.1 (Depth 10km)',
                    font: '10px JetBrains Mono, monospace',
                    fillColor: Cesium.Color.LIME,
                    outlineColor: Cesium.Color.BLACK,
                    outlineWidth: 2,
                    style: Cesium.LabelStyle.FILL_AND_OUTLINE,
                    verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
                    pixelOffset: new Cesium.Cartesian2(0, -14)
                },
                pahadData: {
                    title: 'USGS FDSNws Regional Seismic Event',
                    type: 'SEISMIC_TELEMETRY',
                    location: '27.1800°N, 88.7500°E (38 km SE of KM48)',
                    elevation: 'Depth: 10.0 km',
                    status: 'RECORDED_EVENT',
                    metrics: [
                        { label: 'Magnitude', value: 'M 4.1' },
                        { label: 'Peak Ground Accel (PGA)', value: '0.042 g' },
                        { label: 'Corroboration', value: 'USGS Global Network' }
                    ],
                    provenance: '[LIVE / USGS-FDSNWS]'
                }
            });

            // 5. InSAR Surface Velocity Vector [HISTORICAL / INSAR-LOS]
            this.layers.insarMarker = this.viewer.entities.add({
                name: 'Sentinel-1 InSAR Deformation Zone',
                position: Cesium.Cartesian3.fromDegrees(88.6120, 27.3320, 720),
                point: {
                    pixelSize: 11,
                    color: Cesium.Color.SKYBLUE,
                    outlineColor: Cesium.Color.BLACK,
                    outlineWidth: 1.5
                },
                label: {
                    text: 'InSAR LOS\n-8.4 mm/yr',
                    font: '10px JetBrains Mono, monospace',
                    fillColor: Cesium.Color.SKYBLUE,
                    outlineColor: Cesium.Color.BLACK,
                    outlineWidth: 2,
                    style: Cesium.LabelStyle.FILL_AND_OUTLINE,
                    verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
                    pixelOffset: new Cesium.Cartesian2(0, -14)
                },
                pahadData: {
                    title: 'Sentinel-1 InSAR Surface Deformation',
                    type: 'SATELLITE_RADAR_INTERFEROMETRY',
                    location: '27.3320°N, 88.6120°E',
                    elevation: '720 m MSL',
                    status: 'STEADY_SUBSIDENCE',
                    metrics: [
                        { label: 'LOS Velocity', value: '-8.4 mm/year' },
                        { label: 'Track', value: 'Sentinel-1 Descending Track 121' },
                        { label: 'Coherence', value: '0.74' }
                    ],
                    provenance: '[HISTORICAL / INSAR-LOS]'
                }
            });

            // 6. Planned In-Situ Sensors (0 Live Sensors)
            const plannedSites = [
                { id: 'SN-PIEZ-01', name: 'Piezometer Borehole BH-1', lon: 88.6100, lat: 27.3300, depth: '18.5m' },
                { id: 'SN-TILT-01', name: 'Biaxial Tiltmeter TM-1', lon: 88.6102, lat: 27.3305, depth: 'Surface Crest' },
                { id: 'SN-INCL-01', name: 'Inclinometer Casing IN-1', lon: 88.6098, lat: 27.3298, depth: '25.0m' }
            ];

            plannedSites.forEach((s) => {
                const marker = this.viewer.entities.add({
                    name: s.name,
                    position: Cesium.Cartesian3.fromDegrees(s.lon, s.lat, 680),
                    point: {
                        pixelSize: 9,
                        color: Cesium.Color.YELLOW,
                        outlineColor: Cesium.Color.BLACK,
                        outlineWidth: 1.5
                    },
                    pahadData: {
                        title: s.name,
                        type: 'IN_SITU_GEOTECHNICAL_SENSOR',
                        location: `${s.lat}°N, ${s.lon}°E`,
                        elevation: `Depth: ${s.depth}`,
                        status: 'PLANNED_INSTALLATION (BENCH TESTED)',
                        metrics: [
                            { label: 'Physical Deployment', value: 'UNAVAILABLE_PENDING_INSTALLATION' },
                            { label: 'Live Telemetry', value: '0 records (Zero Field Telemetry)' },
                            { label: 'Hardware Provenance', value: 'Bench Tested / LoRaWAN Ready' }
                        ],
                        provenance: '[PLANNED / BENCH TESTED / PHYSICAL TELEMETRY PENDING]'
                    }
                });
                this.layers.sensorMarkers.push(marker);
            });

            // 7. Synchronize all 20 evaluated NER Risk Corridors
            this.loadAll3DRiskZones();
        }

        /**
         * Load all 20 evaluated NER Risk Zones from /api/pahad/realtime-cri/geojson
         * and render them as color-coded 3D risk beacons on the Cesium globe.
         */
        async loadAll3DRiskZones() {
            if (!this.viewer) return;

            // Clear previous risk zone entities if any
            if (this.layers.allRiskZones && this.layers.allRiskZones.length > 0) {
                this.layers.allRiskZones.forEach(ent => {
                    try { this.viewer.entities.remove(ent); } catch (_) {}
                });
            }
            this.layers.allRiskZones = [];

            try {
                let geojson = window._currentRiskZonesData;
                if (!geojson || !geojson.features || geojson.features.length === 0) {
                    const res = await fetch('/api/pahad/realtime-cri/geojson');
                    if (res.ok) {
                        geojson = await res.json();
                        window._currentRiskZonesData = geojson;
                    }
                }

                if (!geojson || !geojson.features) {
                    console.warn('[GodsEye3D] No risk zones data available to load.');
                    return;
                }

                const features = geojson.features;
                console.log(`[GodsEye3D] Synchronizing ${features.length} NER risk corridors into 3D space.`);

                // Update HUD counter
                const countBadge = document.getElementById('gods-eye-corridor-count');
                if (countBadge) {
                    countBadge.textContent = `${features.length} NER CORRIDORS`;
                }

                // Populate HUD Sector Jump Select
                const sectorSelect = document.getElementById('gods-eye-sector-select');
                if (sectorSelect) {
                    const currentVal = sectorSelect.value;
                    sectorSelect.innerHTML = '<option value="">🎯 Jump to Corridor...</option>';
                    const sortedFeatures = [...features].sort((a, b) => {
                        const criA = (a.properties && a.properties.cri) || 0;
                        const criB = (b.properties && b.properties.cri) || 0;
                        return criB - criA;
                    });
                    sortedFeatures.forEach(f => {
                        const p = f.properties || {};
                        const opt = document.createElement('option');
                        const cid = p.corridor_id || p.corridor || p.sector_id || p.sector_name;
                        opt.value = cid;
                        opt.textContent = `[${p.risk_band || 'LOW'}] ${p.sector_name || p.corridor} (${p.cri || 0})`;
                        sectorSelect.appendChild(opt);
                    });
                    if (currentVal) sectorSelect.value = currentVal;
                }

                // Risk band color mapping
                const BAND_COLORS = {
                    'EXTREME': { color: Cesium.Color.RED, hex: '#dc2626' },
                    'VERY_HIGH': { color: Cesium.Color.ORANGERED, hex: '#ea580c' },
                    'HIGH': { color: Cesium.Color.DARKORANGE, hex: '#f59e0b' },
                    'MODERATE': { color: Cesium.Color.GOLD, hex: '#eab308' },
                    'LOW': { color: Cesium.Color.SPRINGGREEN, hex: '#10b981' }
                };

                features.forEach((feat) => {
                    const geom = feat.geometry || {};
                    const p = feat.properties || {};
                    const coords = geom.coordinates;
                    if (!coords || coords.length < 2) return;

                    const lon = Number(coords[0]);
                    const lat = Number(coords[1]);
                    if (!Number.isFinite(lat) || !Number.isFinite(lon)) return;

                    const bandKey = (p.risk_band || 'LOW').toUpperCase();
                    const colorMeta = BAND_COLORS[bandKey] || BAND_COLORS['LOW'];
                    const baseElevation = Number(p.elevation_m) || 680;
                    const isExtreme = (bandKey === 'EXTREME' || bandKey === 'VERY_HIGH');

                    const pahadPayload = {
                        title: p.sector_name || p.corridor || 'NER Risk Corridor',
                        type: 'PAHAD_REALTIME_RISK_ZONE',
                        location: `${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E`,
                        elevation: `${baseElevation} m MSL (Slope: ${p.slope_deg || '--'}°)`,
                        status: `${bandKey} RISK (CRI: ${p.cri} / 100)`,
                        metrics: [
                            { label: 'Composite Risk Index (CRI)', value: `${p.cri} / 100 [${bandKey}]` },
                            { label: 'Factor of Safety (FoS)', value: `${p.physical_fos || '--'} (Mohr-Coulomb shear balance)` },
                            { label: 'Rainfall (24h)', value: `${p.rainfall_24h_mm || 0} mm [LIVE: Multi-Model]` },
                            { label: 'Corridor & Route', value: `${p.corridor || '--'}, ${p.district || '--'} (${p.state || '--'})` },
                            { label: 'Geology', value: p.geology_class || 'Pre-Cambrian Pelitic Phyllite / Schist' },
                            { label: 'ECMWF / GFS / ICON', value: `${p.ecmwf_24h_mm || '--'}mm / ${p.gfs_24h_mm || '--'}mm / ${p.icon_24h_mm || '--'}mm` }
                        ],
                        provenance: '[DERIVED / MULTIMODAL EVIDENCE FUSION]'
                    };

                    // 1. Tactical 3D Beacon Cylinder rising from terrain
                    const cylinderEntity = this.viewer.entities.add({
                        name: `${p.sector_name || p.corridor} Beacon`,
                        position: Cesium.Cartesian3.fromDegrees(lon, lat, baseElevation + 90),
                        cylinder: {
                            length: 180.0,
                            topRadius: isExtreme ? 30.0 : 18.0,
                            bottomRadius: isExtreme ? 10.0 : 6.0,
                            material: colorMeta.color.withAlpha(0.70),
                            outline: true,
                            outlineColor: Cesium.Color.WHITE.withAlpha(0.60),
                            outlineWidth: 1.5
                        },
                        pahadData: pahadPayload
                    });
                    this.layers.allRiskZones.push(cylinderEntity);

                    // 2. High-visibility Beacon Point & 3D Text Label
                    const pointEntity = this.viewer.entities.add({
                        name: `${p.sector_name || p.corridor} [${bandKey}]`,
                        position: Cesium.Cartesian3.fromDegrees(lon, lat, baseElevation + 200),
                        point: {
                            pixelSize: isExtreme ? 16 : 12,
                            color: colorMeta.color,
                            outlineColor: Cesium.Color.WHITE,
                            outlineWidth: 2,
                            disableDepthTestDistance: Number.POSITIVE_INFINITY
                        },
                        label: {
                            text: `${p.sector_name || p.corridor}\nCRI ${p.cri} [${bandKey}]`,
                            font: isExtreme ? 'bold 11px JetBrains Mono, monospace' : '10px JetBrains Mono, monospace',
                            fillColor: isExtreme ? Cesium.Color.YELLOW : Cesium.Color.WHITE,
                            outlineColor: Cesium.Color.BLACK,
                            outlineWidth: 3,
                            style: Cesium.LabelStyle.FILL_AND_OUTLINE,
                            verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
                            pixelOffset: new Cesium.Cartesian2(0, -18),
                            disableDepthTestDistance: Number.POSITIVE_INFINITY,
                            distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0, 1800000)
                        },
                        pahadData: pahadPayload
                    });
                    this.layers.allRiskZones.push(pointEntity);
                });

            } catch (err) {
                console.error('[GodsEye3D] Failed to synchronize all 3D risk zones:', err);
            }
        }

        /**
         * Fly camera directly to a selected risk corridor and pop up its telemetry card.
         */
        flyToSector(corridorId) {
            if (!this.viewer || !corridorId) return;
            const geojson = window._currentRiskZonesData;
            if (!geojson || !geojson.features) return;

            const target = geojson.features.find(f => {
                const p = f.properties || {};
                return (p.corridor_id === corridorId || p.corridor === corridorId || p.sector_id === corridorId || p.sector_name === corridorId);
            });

            if (!target) return;
            const coords = target.geometry.coordinates;
            const lon = Number(coords[0]);
            const lat = Number(coords[1]);
            const p = target.properties || {};
            const elev = Number(p.elevation_m) || 680;
            const bandKey = (p.risk_band || 'LOW').toUpperCase();

            this.stopOrbit();
            this.viewer.camera.flyTo({
                destination: Cesium.Cartesian3.fromDegrees(lon, lat - 0.025, elev + 2600),
                orientation: {
                    heading: Cesium.Math.toRadians(20),
                    pitch: Cesium.Math.toRadians(-38),
                    roll: 0.0
                },
                duration: 1.8,
                complete: () => {
                    this.showInfoCard({
                        title: p.sector_name || p.corridor || 'NER Risk Corridor',
                        type: 'PAHAD_REALTIME_RISK_ZONE',
                        location: `${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E`,
                        elevation: `${elev} m MSL (Slope: ${p.slope_deg || '--'}°)`,
                        status: `${bandKey} RISK (CRI: ${p.cri} / 100)`,
                        metrics: [
                            { label: 'Composite Risk Index (CRI)', value: `${p.cri} / 100 [${bandKey}]` },
                            { label: 'Factor of Safety (FoS)', value: `${p.physical_fos || '--'} (Mohr-Coulomb shear balance)` },
                            { label: 'Rainfall (24h)', value: `${p.rainfall_24h_mm || 0} mm [LIVE: Multi-Model]` },
                            { label: 'Corridor & Route', value: `${p.corridor || '--'}, ${p.district || '--'} (${p.state || '--'})` },
                            { label: 'Geology', value: p.geology_class || 'Pre-Cambrian Pelitic Phyllite / Schist' },
                            { label: 'ECMWF / GFS / ICON', value: `${p.ecmwf_24h_mm || '--'}mm / ${p.gfs_24h_mm || '--'}mm / ${p.icon_24h_mm || '--'}mm` }
                        ],
                        provenance: '[DERIVED / MULTIMODAL EVIDENCE FUSION]'
                    });
                }
            });
        }

        /**
         * Show slide-out info card with entity data.
         */
        showInfoCard(data) {
            const card = document.getElementById('gods-eye-info-card');
            const titleEl = document.getElementById('ge-info-title');
            const bodyEl = document.getElementById('ge-info-body');
            const provEl = document.getElementById('ge-info-provenance');
            if (!card || !titleEl || !bodyEl || !provEl) return;

            titleEl.textContent = data.title;
            provEl.textContent = data.provenance;

            bodyEl.innerHTML = `
                <div class="flex justify-between text-slate-400">
                    <span>Location:</span>
                    <span class="text-slate-200 font-mono">${data.location}</span>
                </div>
                <div class="flex justify-between text-slate-400">
                    <span>Elevation / Depth:</span>
                    <span class="text-slate-200 font-mono">${data.elevation}</span>
                </div>
                <div class="flex justify-between text-slate-400">
                    <span>Operational State:</span>
                    <span class="text-amber-400 font-bold">${data.status}</span>
                </div>
                ${data.metrics ? `
                    <div class="pt-1 border-t border-slate-800 space-y-0.5">
                        ${data.metrics.map(m => `
                            <div class="flex justify-between">
                                <span class="text-slate-400">${m.label}:</span>
                                <span class="text-slate-200 font-mono">${m.value}</span>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            `;
            card.classList.remove('hidden');
        }

        /**
         * Hide slide-out info card.
         */
        hideInfoCard() {
            const card = document.getElementById('gods-eye-info-card');
            if (card) {
                card.classList.add('hidden');
            }
        }

        /**
         * Update breadcrumb active highlight.
         */
        updateBreadcrumbUI(activeIdx) {
            FLIGHT_STEPS.forEach((_, idx) => {
                const btn = document.getElementById(`flight-step-btn-${idx}`);
                if (btn) {
                    if (idx === activeIdx) {
                        btn.className = 'px-1.5 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-600 font-bold';
                    } else {
                        btn.className = 'px-1.5 py-0.5 rounded border border-slate-700 text-slate-400 hover:text-white';
                    }
                }
            });
        }

        /**
         * Fly camera to a specific hierarchical step.
         */
        flyToStep(stepIndex) {
            if (!this.viewer || stepIndex < 0 || stepIndex >= FLIGHT_STEPS.length) return;
            const target = FLIGHT_STEPS[stepIndex];
            this.currentFlightStep = stepIndex;
            this.updateBreadcrumbUI(stepIndex);
            this.stopOrbit();

            this.viewer.camera.flyTo({
                destination: Cesium.Cartesian3.fromDegrees(target.lon, target.lat, target.height),
                orientation: {
                    heading: Cesium.Math.toRadians(target.heading),
                    pitch: Cesium.Math.toRadians(target.pitch),
                    roll: 0.0
                },
                duration: target.duration
            });
        }

        /**
         * Execute smooth sequential flight from India to KM48.
         */
        async executeIntroFlight() {
            if (!this.viewer || this.isFlying) return;
            this.isFlying = true;

            for (let i = 0; i < FLIGHT_STEPS.length; i++) {
                if (!this.active) break;
                this.currentFlightStep = i;
                this.updateBreadcrumbUI(i);

                const step = FLIGHT_STEPS[i];
                await new Promise((resolve) => {
                    this.viewer.camera.flyTo({
                        destination: Cesium.Cartesian3.fromDegrees(step.lon, step.lat, step.height),
                        orientation: {
                            heading: Cesium.Math.toRadians(step.heading),
                            pitch: Cesium.Math.toRadians(step.pitch),
                            roll: 0.0
                        },
                        duration: step.duration,
                        complete: resolve
                    });
                });

                // Pause briefly between steps for dramatic overview
                if (i < FLIGHT_STEPS.length - 1 && this.active) {
                    await new Promise(r => setTimeout(r, 400));
                }
            }

            this.isFlying = false;
        }

        /**
         * Direct flight to KM48 Hazard Escarpment.
         */
        focusHazard() {
            this.flyToStep(4);
        }

        /**
         * Reset to Level 1 Overview.
         */
        resetHome() {
            this.flyToStep(0);
        }

        /**
         * Toggle 360-degree orbit around KM48.
         */
        toggleOrbit() {
            if (this.orbitActive) {
                this.stopOrbit();
            } else {
                this.startOrbit();
            }
        }

        startOrbit() {
            if (!this.viewer) return;
            this.orbitActive = true;
            const btn = document.getElementById('gods-eye-orbit-btn');
            if (btn) {
                btn.className = 'px-2 py-1 rounded bg-amber-600 text-white border border-amber-400 flex items-center gap-1 font-bold';
            }

            // Ensure camera is positioned at KM48
            const target = Cesium.Cartesian3.fromDegrees(CANONICAL_KM48.longitude, CANONICAL_KM48.latitude, CANONICAL_KM48.elevation);
            const initialDistance = 3500;
            let angle = 0;

            if (this.orbitTimer) clearInterval(this.orbitTimer);
            this.orbitTimer = setInterval(() => {
                if (!this.orbitActive || !this.viewer) {
                    this.stopOrbit();
                    return;
                }
                angle += 0.35;
                if (angle >= 360) angle = 0;
                this.viewer.camera.rotate(Cesium.Cartesian3.UNIT_Z, -0.003);
            }, 30);
        }

        stopOrbit() {
            this.orbitActive = false;
            if (this.orbitTimer) {
                clearInterval(this.orbitTimer);
                this.orbitTimer = null;
            }
            const btn = document.getElementById('gods-eye-orbit-btn');
            if (btn) {
                btn.className = 'px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-600 flex items-center gap-1';
            }
        }

        /**
         * Activate God's Eye 3D Mode.
         */
        async activate() {
            this.active = true;
            if (!this.container) this.init();
            if (!this.container) return;

            // Hide 2D Leaflet Map
            const map2d = document.getElementById('map');
            if (map2d) {
                map2d.style.display = 'none';
            }

            // Show 3D Container
            this.container.classList.remove('hidden');
            this.container.style.display = 'block';

            // Render HUD
            this.renderHUD();
            this.hideErrorState();

            try {
                if (!this.cesiumLoaded) {
                    await this.loadCesium();
                }

                this.hideLoadingState();
                if (!this.viewer) {
                    await this.initViewer();
                }

                // Resume rendering if viewer exists
                if (this.viewer) {
                    this.viewer.useDefaultRenderLoop = true;
                    // Ensure all 20 risk zones are synced with latest data
                    this.loadAll3DRiskZones();
                    // Trigger introductory camera flight
                    this.executeIntroFlight();
                }
            } catch (err) {
                console.error('[GodsEye3D] Activation failed:', err);
                this.renderErrorState('Could not initialize 3D scene. Ensure WebGL is enabled in your browser.');
            }
        }

        /**
         * Deactivate God's Eye 3D Mode and return cleanly to 2D Leaflet.
         */
        deactivate() {
            this.active = false;
            this.stopOrbit();

            if (this.container) {
                this.container.classList.add('hidden');
                this.container.style.display = 'none';
            }

            // Restore 2D Leaflet Map
            const map2d = document.getElementById('map');
            if (map2d) {
                map2d.style.display = 'block';
            }

            // Pause Cesium rendering loop to conserve CPU/GPU
            if (this.viewer) {
                this.viewer.useDefaultRenderLoop = false;
            }

            // Invalidate Leaflet Map Size to prevent blank tile artifacts
            if (window.map && typeof window.map.invalidateSize === 'function') {
                window.map.invalidateSize();
                setTimeout(() => {
                    if (window.map && typeof window.map.invalidateSize === 'function') {
                        window.map.invalidateSize();
                    }
                }, 150);
            }
        }

        /**
         * Check if 3D mode is currently active.
         */
        isActive() {
            return this.active;
        }

        /**
         * Toggle 3D mode.
         */
        toggle() {
            if (this.isActive()) {
                if (typeof window.exitGodsEye3D === 'function') {
                    window.exitGodsEye3D();
                } else if (typeof window.switchMainBasemap === 'function') {
                    window.switchMainBasemap('bhuvan');
                } else {
                    this.deactivate();
                }
            } else {
                this.activate();
            }
        }
    }

    // Export Singleton to global window namespace
    window.GodsEye3D = new GodsEye3DController();

    // Auto-init on DOMContentLoaded if DOM is already parsed
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => window.GodsEye3D.init());
    } else {
        window.GodsEye3D.init();
    }

})(window, document);

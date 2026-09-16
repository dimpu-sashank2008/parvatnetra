/**
 * static/js/pahad_gis_animation.js
 * ================================
 * PARVAT NETRA • PAHAD AI — Temporal GIS Hazard Map Animation & Dynamic Risk Halo
 * Phase 12 Visual Intelligence Upgrade
 * 
 * Features:
 *   1. Dynamic CRI-Driven Risk Halo: Smooth radius, opacity, and pulse scaling.
 *   2. Multi-Temporal Playback: 24H AGO -> 12H AGO -> 6H AGO -> NOW.
 *   3. Strict Provenance Integrity: [LIVE] vs [SIMULATED] vs [HISTORICAL].
 *   4. Multi-Corridor Support: Agnostic to any canonical corridor with isolation.
 *   5. Performance & Layer Reuse: Updates existing Leaflet layers without thrashing.
 *   6. Reduced-Motion Support: Disables pulsing when prefers-reduced-motion is active.
 *   7. Click-to-Explain: Connects directly to PAHAD Decision Intelligence breakdown.
 */

(function(window) {
    'use strict';

    class PahadGisAnimationController {
        constructor() {
            this.map = null;
            this.currentCorridorId = 'SK-NH10-KM48';
            this.currentMode = 'live'; // 'live' | 'scenario' | 'historical'
            this.temporalData = null;
            this.currentStepIndex = 0;
            this.isPlaying = false;
            this.playIntervalTimer = null;
            this.stepDurationMs = 2800;

            // Leaflet layers
            this.haloCircle = null;
            this.coreCircle = null;
            this.corridorLine = null;
            this.animationPane = null;

            // State
            this.prefersReducedMotion = false;
            this.isCollapsed = false;
        }

        init(leafletMap) {
            if (!leafletMap) return;
            this.map = leafletMap;

            // Check reduced motion
            try {
                const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
                this.prefersReducedMotion = mediaQuery.matches;
                mediaQuery.addEventListener('change', (e) => {
                    this.prefersReducedMotion = e.matches;
                    this.applyCurrentStepVisuals();
                });
            } catch (e) {
                this.prefersReducedMotion = false;
            }

            // Create dedicated pane for animation so it floats above base tiles & NER borders, below markers
            if (this.map.createPane && !this.map.getPane('pahadHazardAnimationPane')) {
                this.animationPane = this.map.createPane('pahadHazardAnimationPane');
                this.animationPane.style.zIndex = 380;
                this.animationPane.style.pointerEvents = 'auto';
            }

            this.injectStyles();
            this.createTimelineWidget();
            this.hookCorridorSelection();

            try {
                this.isCollapsed = localStorage.getItem('pahad_gis_anim_collapsed') === '1';
                this.updateCollapseUI();
            } catch (_) {}

            // Initial load for active corridor
            const activeId = window.currentSelectedSectorId || 'SK-NH10-KM48';
            this.loadCorridorData(activeId, 'live', false);
        }

        injectStyles() {
            if (document.getElementById('pahad-gis-anim-styles')) return;
            const style = document.createElement('style');
            style.id = 'pahad-gis-anim-styles';
            style.textContent = `
                @keyframes pahad-halo-pulse-critical {
                    0% { stroke-opacity: 0.85; stroke-width: 3.5px; }
                    50% { stroke-opacity: 0.25; stroke-width: 1.5px; }
                    100% { stroke-opacity: 0.85; stroke-width: 3.5px; }
                }
                @keyframes pahad-halo-pulse-high {
                    0% { stroke-opacity: 0.75; stroke-width: 3.0px; }
                    50% { stroke-opacity: 0.35; stroke-width: 1.8px; }
                    100% { stroke-opacity: 0.75; stroke-width: 3.0px; }
                }
                @keyframes pahad-halo-breathing-moderate {
                    0% { stroke-opacity: 0.60; stroke-width: 2.2px; }
                    50% { stroke-opacity: 0.30; stroke-width: 1.5px; }
                    100% { stroke-opacity: 0.60; stroke-width: 2.2px; }
                }
                .pahad-anim-halo-extreme path {
                    animation: pahad-halo-pulse-critical 2.0s infinite ease-in-out;
                }
                .pahad-anim-halo-high path {
                    animation: pahad-halo-pulse-high 3.8s infinite ease-in-out;
                }
                .pahad-anim-halo-moderate path {
                    animation: pahad-halo-breathing-moderate 8.0s infinite ease-in-out;
                }
                .pahad-anim-halo-low path {
                    animation: none;
                }
                @media (prefers-reduced-motion: reduce) {
                    .pahad-anim-halo-extreme path,
                    .pahad-anim-halo-high path,
                    .pahad-anim-halo-moderate path {
                        animation: none !important;
                    }
                }
                #pahad-gis-timeline-control {
                    box-shadow: 0 4px 20px rgba(0,0,0,0.45);
                    backdrop-filter: blur(8px);
                }
                #anim-widget-header:hover #anim-widget-title {
                    color: #38bdf8;
                }
            `;
            document.head.appendChild(style);
        }

        hookCorridorSelection() {
            const existingHandler = window.onCorridorSelectionChanged;
            const self = this;
            window.onCorridorSelectionChanged = async function(sectorId, shouldZoom = true) {
                if (typeof existingHandler === 'function') {
                    try {
                        await existingHandler(sectorId, shouldZoom);
                    } catch (err) {
                        console.warn('[GIS-ANIM] Wrapped handler error:', err);
                    }
                }
                self.onCorridorChanged(sectorId, shouldZoom);
            };
        }

        onCorridorChanged(sectorId, shouldZoom = false) {
            if (!sectorId) return;
            const isDifferent = sectorId !== this.currentCorridorId;
            if (isDifferent) {
                this.pause();
                this.currentCorridorId = sectorId;
                this.loadCorridorData(sectorId, 'live', shouldZoom === true);
            }
        }

        async loadCorridorData(corridorId, mode = 'live', flyTo = false) {
            this.currentCorridorId = corridorId;
            this.currentMode = mode;
            this.updateLoadingState(true);

            try {
                const url = `/api/pahad/temporal-risk?corridor_id=${encodeURIComponent(corridorId)}&mode=${encodeURIComponent(mode)}`;
                const res = await fetch(url, { cache: 'no-store' });
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                const data = await res.json();
                this.temporalData = data;

                // Reset step index (last step for live, step 0 for playback drills)
                if (mode === 'live') {
                    this.currentStepIndex = Math.max(0, (data.timeline || []).length - 1);
                } else {
                    this.currentStepIndex = 0;
                }

                this.renderWidgetContent();
                this.applyCurrentStepVisuals();

                if (flyTo && this.map && data.latitude && data.longitude) {
                    try {
                        if (this.map._loaded && typeof this.map.panTo === 'function') {
                            this.map.panTo([data.latitude, data.longitude], { animate: true, duration: 0.8 });
                        }
                    } catch (_) {}
                }
                return data;
            } catch (err) {
                console.error('[GIS-ANIM] Failed to load temporal risk data:', err);
                this.renderErrorState(err.message);
                throw err;
            } finally {
                this.updateLoadingState(false);
            }
        }

        createTimelineWidget() {
            if (document.getElementById('pahad-gis-timeline-control')) return;

            const mapContainer = document.getElementById('gis-map') || document.getElementById('map');
            if (!mapContainer) return;

            const widget = document.createElement('div');
            widget.id = 'pahad-gis-timeline-control';
            widget.className = 'absolute bottom-3 left-[54px] sm:left-[58px] z-[450] bg-[#070B10]/95 border border-[#1E293B] rounded-md p-2 sm:p-2.5 text-white max-w-[340px] sm:max-w-[380px] w-[calc(100%-70px)] transition-all select-none shadow-2xl';
            widget.innerHTML = `
                <!-- Header (Clickable to toggle collapse) -->
                <div id="anim-widget-header" class="flex items-center justify-between gap-2 cursor-pointer pb-1.5 border-b border-slate-800/80 transition-colors" title="Click to collapse/expand timeline">
                    <div class="flex items-center gap-1.5 min-w-0">
                        <i class="ph-bold ph-chart-polar text-sky-400 text-xs shrink-0"></i>
                        <span class="text-[10px] sm:text-[11px] font-black tracking-wider uppercase text-slate-200 shrink-0" id="anim-widget-title">RISK EVOLUTION</span>
                        <span id="anim-collapsed-summary" class="hidden text-[9px] font-mono font-bold text-slate-300 truncate max-w-[200px]"></span>
                    </div>
                    <div class="flex items-center gap-1.5 shrink-0">
                        <span id="anim-provenance-badge" class="text-[9px] font-mono font-bold px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">[LIVE]</span>
                        <button type="button" id="btn-anim-collapse" class="p-0.5 sm:p-1 rounded text-slate-400 hover:text-white hover:bg-slate-800/70 transition flex items-center justify-center focus:outline-none focus:ring-1 focus:ring-sky-500" title="Collapse timeline" aria-label="Collapse timeline control" aria-expanded="true">
                            <i id="anim-collapse-icon" class="ph-bold ph-caret-down text-xs"></i>
                        </button>
                    </div>
                </div>

                <!-- Collapsible Body -->
                <div id="anim-widget-body" class="mt-2 space-y-2 transition-all">
                    <!-- Mode Switcher (Live vs Scenario vs Historical) -->
                    <div class="flex items-center gap-1">
                        <button type="button" id="btn-anim-mode-live" onclick="window.PahadGisAnimation.switchMode('live')" class="flex-1 py-1 px-2 text-[10px] font-bold rounded bg-sky-950 text-sky-200 border border-sky-600 transition" title="Inspect Authoritative Live Runtime State">
                            LIVE NOW
                        </button>
                        <button type="button" id="btn-anim-mode-scen" onclick="window.PahadGisAnimation.switchMode('scenario')" class="flex-1 py-1 px-2 text-[10px] font-bold rounded bg-slate-900 text-slate-400 border border-slate-700 hover:text-white transition" title="Play Physics-Calibrated Monsoon Failure Drill">
                            SCENARIO DRILL
                        </button>
                        <button type="button" id="btn-anim-mode-hist" onclick="window.PahadGisAnimation.switchMode('historical')" class="py-1 px-2 text-[10px] font-bold rounded bg-slate-900 text-slate-400 border border-slate-700 hover:text-white transition hidden" title="Inspect Documented Historical Event">
                            HISTORICAL
                        </button>
                    </div>

                    <!-- Telemetry Readout Bar -->
                    <div id="anim-telemetry-bar" class="grid grid-cols-4 gap-1.5 p-1.5 bg-[#0A101D] border border-slate-800 rounded font-mono text-center">
                        <div>
                            <span class="text-[8px] uppercase text-slate-500 block">TIME</span>
                            <strong id="anim-val-time" class="text-[10px] text-slate-200 font-bold">NOW</strong>
                        </div>
                        <div>
                            <span class="text-[8px] uppercase text-slate-500 block">CRI</span>
                            <strong id="anim-val-cri" class="text-[10px] text-sky-400 font-bold">--</strong>
                        </div>
                        <div>
                            <span class="text-[8px] uppercase text-slate-500 block">FoS</span>
                            <strong id="anim-val-fos" class="text-[10px] text-amber-400 font-bold">--</strong>
                        </div>
                        <div>
                            <span class="text-[8px] uppercase text-slate-500 block">BAND</span>
                            <strong id="anim-val-band" class="text-[9px] text-emerald-400 font-bold">--</strong>
                        </div>
                    </div>

                    <!-- Step Buttons & Play/Pause -->
                    <div class="flex items-center gap-1.5">
                        <button type="button" id="btn-anim-play" onclick="window.PahadGisAnimation.togglePlay()" class="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-white rounded text-[10px] font-bold border border-slate-600 flex items-center gap-1 shrink-0" aria-label="Play or pause hazard evolution">
                            <i id="anim-play-icon" class="ph-bold ph-play"></i>
                            <span id="anim-play-label">Play</span>
                        </button>
                        <div id="anim-steps-container" class="flex items-center gap-1 flex-grow overflow-x-auto">
                            <!-- Rendered dynamically -->
                        </div>
                    </div>
                </div>
            `;

            const header = widget.querySelector('#anim-widget-header');
            if (header) {
                header.addEventListener('click', (e) => {
                    this.toggleCollapse(e);
                });
            }

            if (window.L && window.L.DomEvent) {
                window.L.DomEvent.disableClickPropagation(widget);
                window.L.DomEvent.disableScrollPropagation(widget);
            }

            mapContainer.appendChild(widget);
            this.updateCollapseUI();
        }

        toggleCollapse(e) {
            if (e && typeof e.stopPropagation === 'function') {
                e.stopPropagation();
            }
            this.isCollapsed = !this.isCollapsed;
            try {
                localStorage.setItem('pahad_gis_anim_collapsed', this.isCollapsed ? '1' : '0');
            } catch (_) {}
            this.updateCollapseUI();
        }

        updateCollapseUI() {
            const widget = document.getElementById('pahad-gis-timeline-control');
            const header = document.getElementById('anim-widget-header');
            const body = document.getElementById('anim-widget-body');
            const icon = document.getElementById('anim-collapse-icon');
            const btn = document.getElementById('btn-anim-collapse');
            const summary = document.getElementById('anim-collapsed-summary');

            if (!widget || !body) return;

            if (this.isCollapsed) {
                body.classList.add('hidden');
                if (header) {
                    header.classList.remove('border-b', 'border-slate-800/80', 'pb-1.5');
                    header.setAttribute('title', 'Click to expand timeline');
                }
                widget.classList.remove('w-[calc(100%-70px)]');
                widget.classList.add('w-auto', 'max-w-[440px]');
                if (icon) icon.className = 'ph-bold ph-caret-up text-xs';
                if (btn) {
                    btn.title = 'Expand timeline';
                    btn.setAttribute('aria-label', 'Expand timeline control');
                    btn.setAttribute('aria-expanded', 'false');
                }
                if (summary) {
                    summary.classList.remove('hidden');
                }
                this.updateCollapsedSummary();
            } else {
                body.classList.remove('hidden');
                if (header) {
                    header.classList.add('border-b', 'border-slate-800/80', 'pb-1.5');
                    header.setAttribute('title', 'Click to collapse timeline');
                }
                widget.classList.remove('w-auto', 'max-w-[440px]');
                widget.classList.add('w-[calc(100%-70px)]');
                if (icon) icon.className = 'ph-bold ph-caret-down text-xs';
                if (btn) {
                    btn.title = 'Collapse timeline';
                    btn.setAttribute('aria-label', 'Collapse timeline control');
                    btn.setAttribute('aria-expanded', 'true');
                }
                if (summary) {
                    summary.classList.add('hidden');
                }
            }
        }

        updateCollapsedSummary() {
            const summary = document.getElementById('anim-collapsed-summary');
            if (!summary) return;
            if (this.temporalData && Array.isArray(this.temporalData.timeline) && this.temporalData.timeline.length > 0) {
                const step = this.temporalData.timeline[this.currentStepIndex] || this.temporalData.timeline[0];
                if (step) {
                    const criStr = Number.isFinite(step.cri) ? step.cri.toFixed(1) : '--';
                    const band = step.risk_band || 'LOW';
                    summary.innerHTML = `<span class="text-slate-500 font-normal">|</span> <span style="color:${step.color || '#38bdf8'}">${step.label}: CRI ${criStr} [${band}]</span>`;
                    return;
                }
            }
            summary.innerHTML = '';
        }

        renderWidgetContent() {
            if (!this.temporalData) return;
            const data = this.temporalData;

            const liveBtn = document.getElementById('btn-anim-mode-live');
            const scenBtn = document.getElementById('btn-anim-mode-scen');
            const histBtn = document.getElementById('btn-anim-mode-hist');
            const provBadge = document.getElementById('anim-provenance-badge');
            const playBtn = document.getElementById('btn-anim-play');

            if (liveBtn && scenBtn && histBtn) {
                liveBtn.className = this.currentMode === 'live'
                    ? 'flex-1 py-1 px-2 text-[10px] font-bold rounded bg-sky-950 text-sky-200 border border-sky-600 transition'
                    : 'flex-1 py-1 px-2 text-[10px] font-bold rounded bg-slate-900 text-slate-400 border border-slate-700 hover:text-white transition';
                
                scenBtn.className = this.currentMode === 'scenario'
                    ? 'flex-1 py-1 px-2 text-[10px] font-bold rounded bg-amber-950 text-amber-200 border border-amber-600 transition'
                    : 'flex-1 py-1 px-2 text-[10px] font-bold rounded bg-slate-900 text-slate-400 border border-slate-700 hover:text-white transition';

                if (data.historical_available) {
                    histBtn.classList.remove('hidden');
                    histBtn.className = this.currentMode === 'historical'
                        ? 'py-1 px-2 text-[10px] font-bold rounded bg-rose-950 text-rose-200 border border-rose-600 transition'
                        : 'py-1 px-2 text-[10px] font-bold rounded bg-slate-900 text-slate-400 border border-slate-700 hover:text-white transition';
                } else {
                    histBtn.classList.add('hidden');
                }
            }

            if (provBadge) {
                provBadge.textContent = data.provenance || '[LIVE]';
                if (data.provenance === '[LIVE]') {
                    provBadge.className = 'text-[9px] font-mono font-bold px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800';
                } else if (data.provenance === '[SIMULATED]') {
                    provBadge.className = 'text-[9px] font-mono font-bold px-1.5 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800';
                } else {
                    provBadge.className = 'text-[9px] font-mono font-bold px-1.5 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800';
                }
            }

            const stepsContainer = document.getElementById('anim-steps-container');
            if (stepsContainer && Array.isArray(data.timeline)) {
                stepsContainer.innerHTML = data.timeline.map((step, idx) => {
                    const isActive = idx === this.currentStepIndex;
                    const activeClass = isActive
                        ? 'bg-sky-600 text-white font-bold border-sky-400 shadow-sm'
                        : 'bg-slate-900 text-slate-400 hover:text-slate-200 border-slate-800';
                    return `
                        <button type="button" onclick="window.PahadGisAnimation.goToStep(${idx})" class="flex-1 py-1 px-1.5 text-[9px] font-mono uppercase rounded border transition truncate text-center ${activeClass}" title="${step.label} (${step.risk_band})">
                            ${step.label}
                        </button>
                    `;
                }).join('');
            }

            if (playBtn) {
                if (!data.timeline || data.timeline.length <= 1) {
                    playBtn.disabled = true;
                    playBtn.classList.add('opacity-50', 'cursor-not-allowed');
                } else {
                    playBtn.disabled = false;
                    playBtn.classList.remove('opacity-50', 'cursor-not-allowed');
                }
            }
            this.updateCollapsedSummary();
        }

        applyCurrentStepVisuals() {
            if (!this.map || !this.temporalData || !this.temporalData.timeline) return;
            const timeline = this.temporalData.timeline;
            if (this.currentStepIndex >= timeline.length) {
                this.currentStepIndex = 0;
            }
            const step = timeline[this.currentStepIndex];
            if (!step) return;

            const timeEl = document.getElementById('anim-val-time');
            const criEl = document.getElementById('anim-val-cri');
            const fosEl = document.getElementById('anim-val-fos');
            const bandEl = document.getElementById('anim-val-band');

            if (timeEl) timeEl.textContent = step.label;
            if (criEl) {
                criEl.textContent = Number.isFinite(step.cri) ? step.cri.toFixed(1) : '--';
                criEl.style.color = step.color || '#38bdf8';
            }
            if (fosEl) {
                fosEl.textContent = Number.isFinite(step.fos) ? step.fos.toFixed(3) : '--';
                fosEl.style.color = step.fos < 1.0 ? '#f87171' : (step.fos < 1.3 ? '#fbbf24' : '#34d399');
            }
            if (bandEl) {
                bandEl.textContent = step.risk_band || 'LOW';
                bandEl.style.color = step.color || '#34d399';
            }
            this.updateCollapsedSummary();

            const stepsContainer = document.getElementById('anim-steps-container');
            if (stepsContainer) {
                const buttons = stepsContainer.querySelectorAll('button');
                buttons.forEach((btn, idx) => {
                    if (idx === this.currentStepIndex) {
                        btn.className = 'flex-1 py-1 px-1.5 text-[9px] font-mono uppercase rounded border transition truncate text-center bg-sky-600 text-white font-bold border-sky-400 shadow-sm';
                    } else {
                        btn.className = 'flex-1 py-1 px-1.5 text-[9px] font-mono uppercase rounded border transition truncate text-center bg-slate-900 text-slate-400 hover:text-slate-200 border-slate-800';
                    }
                });
            }

            const lat = this.temporalData.latitude;
            const lon = this.temporalData.longitude;
            if (!lat || !lon || !window.L) return;

            const radiusM = step.halo_radius_m || 500;
            const color = step.color || '#38bdf8';
            const opacity = step.halo_opacity || 0.35;
            const band = step.risk_band || 'LOW';

            let pulseClass = 'pahad-anim-halo-low';
            if (!this.prefersReducedMotion) {
                if (band === 'EXTREME') pulseClass = 'pahad-anim-halo-extreme';
                else if (band === 'VERY HIGH' || band === 'HIGH') pulseClass = 'pahad-anim-halo-high';
                else if (band === 'MODERATE') pulseClass = 'pahad-anim-halo-moderate';
            }

            if (!this.haloCircle) {
                this.haloCircle = window.L.circle([lat, lon], {
                    radius: radiusM,
                    pane: 'pahadHazardAnimationPane',
                    color: color,
                    weight: step.border_weight || 2.0,
                    opacity: 0.85,
                    fillColor: color,
                    fillOpacity: opacity,
                    className: pulseClass
                }).addTo(this.map);

                this.haloCircle.on('click', () => {
                    this.showExplanationModal(step);
                });
                this.haloCircle.bindTooltip(`<b>${this.temporalData.corridor_name}</b><br>State: ${step.label}<br>CRI: ${step.cri} [${step.risk_band}]<br><span style="font-size:9px;color:#38bdf8">Click to inspect causal breakdown</span>`, { sticky: true });
            } else {
                this.haloCircle.setLatLng([lat, lon]);
                this.haloCircle.setRadius(radiusM);
                this.haloCircle.setStyle({
                    color: color,
                    weight: step.border_weight || 2.0,
                    fillColor: color,
                    fillOpacity: opacity,
                    className: pulseClass
                });
                this.haloCircle.setTooltipContent(`<b>${this.temporalData.corridor_name}</b><br>State: ${step.label}<br>CRI: ${step.cri} [${step.risk_band}]<br><span style="font-size:9px;color:#38bdf8">Click to inspect causal breakdown</span>`);
            }

            const coreRadius = Math.max(80, Math.round(radiusM * 0.35));
            if (!this.coreCircle) {
                this.coreCircle = window.L.circle([lat, lon], {
                    radius: coreRadius,
                    pane: 'pahadHazardAnimationPane',
                    color: color,
                    weight: 2.0,
                    opacity: 0.95,
                    fillColor: color,
                    fillOpacity: Math.min(0.85, opacity + 0.25)
                }).addTo(this.map);
                this.coreCircle.on('click', () => {
                    this.showExplanationModal(step);
                });
            } else {
                this.coreCircle.setLatLng([lat, lon]);
                this.coreCircle.setRadius(coreRadius);
                this.coreCircle.setStyle({
                    color: color,
                    weight: 2.0,
                    fillColor: color,
                    fillOpacity: Math.min(0.85, opacity + 0.25)
                });
            }
        }

        showExplanationModal(step) {
            const name = this.temporalData.corridor_name;
            const cri = step.cri;
            const fos = step.fos;
            const rain = step.rainfall_mm;
            const band = step.risk_band;
            const prov = step.provenance || '[LIVE]';

            if (typeof window.showToast === 'function') {
                window.showToast(`Inspecting Hazard Zone: ${name} (CRI: ${cri}, FoS: ${fos})`, 'info');
            }

            const cardZone = document.getElementById('card-zone-title');
            const cardSub = document.getElementById('card-zone-sub');
            const cardBadge = document.getElementById('card-risk-badge');
            const evRain = document.getElementById('ev-rain');
            const cardDriver = document.getElementById('card-driver');

            if (cardZone) cardZone.textContent = name;
            if (cardSub) cardSub.textContent = `${this.temporalData.district} | ${this.temporalData.state} (${step.label})`;
            if (cardBadge) {
                cardBadge.textContent = `${band} (${step.label})`;
                cardBadge.style.color = step.color || '#f87171';
            }
            if (evRain) evRain.textContent = `${rain.toFixed(1)} mm (${step.label})`;
            if (cardDriver && step.drivers && step.drivers.length > 0) {
                cardDriver.textContent = `${step.drivers[0].feature} [${step.drivers[0].direction}]`;
            }

            if (this.haloCircle) {
                this.haloCircle.bindPopup(`
                    <div style="font-size:11px;font-family:Inter,sans-serif;line-height:1.4;min-width:210px;">
                        <span style="font-size:9px;font-family:monospace;font-weight:bold;color:${step.color};">${prov} &bull; ${step.label}</span>
                        <h4 style="margin:2px 0 4px;font-weight:800;color:#0F172A;">${name}</h4>
                        <div style="background:#F1F5F9;padding:4px 6px;border-radius:4px;margin-bottom:6px;">
                            <div><b>CRI:</b> <span style="font-family:monospace;font-weight:bold;color:${step.color};">${cri}</span> / 100 [${band}]</div>
                            <div><b>FoS:</b> <span style="font-family:monospace;font-weight:bold;">${fos}</span></div>
                            <div><b>Rain:</b> <span style="font-family:monospace;">${rain} mm</span></div>
                        </div>
                        <div style="font-size:10px;color:#334155;margin-bottom:4px;">
                            <b>Contributing Drivers:</b><br>
                            ${(step.drivers || []).map(d => `&bull; ${d.feature}`).join('<br>') || '&bull; Slope saturation'}
                        </div>
                        <div style="border-top:1px solid #E2E8F0;padding-top:4px;font-size:9px;color:#64748B;">
                            Authority Review &bull; Zero Siren Dispatch
                        </div>
                    </div>
                `, { maxWidth: 280 }).openPopup();
            }
        }

        switchMode(mode) {
            if (this.currentMode === mode) return Promise.resolve(this.temporalData);
            this.pause();
            return this.loadCorridorData(this.currentCorridorId, mode, false);
        }

        goToStep(stepIndex) {
            this.currentStepIndex = stepIndex;
            this.applyCurrentStepVisuals();
        }

        togglePlay() {
            if (this.isPlaying) {
                this.pause();
            } else {
                this.play();
            }
        }

        play() {
            if (!this.temporalData || !this.temporalData.timeline || this.temporalData.timeline.length <= 1) return;
            this.isPlaying = true;

            const icon = document.getElementById('anim-play-icon');
            const label = document.getElementById('anim-play-label');
            if (icon) icon.className = 'ph-bold ph-pause';
            if (label) label.textContent = 'Pause';

            clearInterval(this.playIntervalTimer);
            this.playIntervalTimer = setInterval(() => {
                const total = this.temporalData.timeline.length;
                this.currentStepIndex = (this.currentStepIndex + 1) % total;
                this.applyCurrentStepVisuals();
            }, this.stepDurationMs);
        }

        pause() {
            this.isPlaying = false;
            clearInterval(this.playIntervalTimer);
            this.playIntervalTimer = null;

            const icon = document.getElementById('anim-play-icon');
            const label = document.getElementById('anim-play-label');
            if (icon) icon.className = 'ph-bold ph-play';
            if (label) label.textContent = 'Play';
        }

        updateLoadingState(isLoading) {
            const timeEl = document.getElementById('anim-val-time');
            if (timeEl && isLoading) {
                timeEl.textContent = '...';
            }
        }

        renderErrorState(errMsg) {
            const bar = document.getElementById('anim-telemetry-bar');
            if (bar) {
                bar.innerHTML = `<div class="col-span-4 text-rose-400 text-[10px]">Error loading temporal data</div>`;
            }
        }

        destroy() {
            this.pause();
            if (this.haloCircle && this.map) this.map.removeLayer(this.haloCircle);
            if (this.coreCircle && this.map) this.map.removeLayer(this.coreCircle);
            this.haloCircle = null;
            this.coreCircle = null;
        }
    }

    // Global Singleton
    window.PahadGisAnimation = new PahadGisAnimationController();

    // Auto-init when map is ready
    if (document.readyState === 'complete' || document.readyState === 'interactive') {
        setTimeout(checkMapAndInit, 300);
    } else {
        window.addEventListener('DOMContentLoaded', () => setTimeout(checkMapAndInit, 300));
    }

    function checkMapAndInit() {
        if (window.map && typeof window.map.getCenter === 'function') {
            window.PahadGisAnimation.init(window.map);
        } else {
            let retries = 0;
            const timer = setInterval(() => {
                retries++;
                if (window.map && typeof window.map.getCenter === 'function') {
                    clearInterval(timer);
                    window.PahadGisAnimation.init(window.map);
                } else if (retries > 20) {
                    clearInterval(timer);
                }
            }, 250);
        }
    }

})(window);

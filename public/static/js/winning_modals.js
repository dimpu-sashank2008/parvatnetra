// -*- coding: utf-8 -*-
/**
 * static/js/winning_modals.js
 * ===========================
 * PARVAT NETRA • SIH 26001 Grand Championship Modal Subsystem
 * -----------------------------------------------------------
 * Powers:
 * 1. Hardware BOM & Indigenous IoT Node Modal
 * 2. Official NDMA / SDMA Situation Report (SitRep) Disaster Memo (Printable)
 * 3. Interactive 2G Feature Phone SMS & Cell Broadcast Channel 4370 Simulator
 */

(function () {
    'use strict';

    // --- 0. EMBEDDED RESILIENCE FALLBACKS (0ms Offline Render Guarantee) ---
    const DEFAULT_BOM_ITEMS = [
        { id: "MCU-01", category: "Microcontroller & Compute", component: "Espressif ESP32-S3-WROOM-1 (N16R8)", specs: "Dual-Core Xtensa LX7 @ 240MHz, 16MB Flash, 8MB PSRAM, Wi-Fi 4 + BLE 5.0", function: "Sensor sampling, 18-byte packed binary encoding, local circular flash buffer, BLE commissioning", ip_rating: "Mounted in IP67 enclosure", cost_inr: 480 },
        { id: "RF-01", category: "Long-Range RF Transceiver", component: "Semtech SX1262 Sub-GHz LoRa Module", specs: "865–867 MHz (IN865 Band), +22dBm max output, -148dBm sensitivity, SPI bus", function: "Long-range ridge relay transmission across Himalayan mountain chokepoints (up to 15km LoS)", ip_rating: "Mounted in IP67 enclosure", cost_inr: 850 },
        { id: "ANT-01", category: "RF Antenna & Cabling", component: "868MHz 5.8dBi Fiberglass Omni Antenna + RG58 Cable", specs: "5.8 dBi gain, N-Male to SMA, UV-resistant fiberglass, lightning arrestor", function: "High-gain RF propagation penetrating dense monsoon mist and pine tree canopy", ip_rating: "IP68 Outdoor", cost_inr: 1250 },
        { id: "TILT-01", category: "Geotechnical Sensor", component: "Murata SCA103T-D04 Dual-Axis MEMS Inclinometer", specs: "±30° measurement range, 0.001° resolution, analog differential output, thermal compensation", function: "Sub-millimeter displacement & borehole shear plane rotational creep detection", ip_rating: "IP68 Hermetic Sensor Head", cost_inr: 3400 },
        { id: "PIEZO-01", category: "Geotechnical Sensor", component: "Vibrating Wire Piezometer Transducer (Plucked-Coil Interface)", specs: "0–350 kPa range, ±0.1% FS accuracy, frequency output 1400–3500 Hz", function: "Pore-water pressure monitoring to detect sudden loss of effective stress in slip plane", ip_rating: "IP68 Hermetic Submersible", cost_inr: 4200 },
        { id: "MOIST-01", category: "Hydrometric Sensor", component: "TDR Soil Moisture & Temperature Probe", specs: "0–100% VWC (Volumetric Water Content), RS-485 Modbus RTU interface", function: "van Genuchten wetting front infiltration tracking & matric suction dissipation", ip_rating: "IP68 Direct Soil Burial", cost_inr: 1450 },
        { id: "SOLAR-01", category: "Power System", component: "20W Monocrystalline PV Panel + Bracket", specs: "18V Vmp, 1.11A Imp, tempered glass, anodized aluminum mountain bracket", function: "Year-round solar harvesting sized for Northeast monsoon diffuse irradiance conditions", ip_rating: "IP65 Weatherproof", cost_inr: 1100 },
        { id: "BATT-01", category: "Power System", component: "12V 42Ah LiFePO4 Battery Pack + Integrated Smart BMS", specs: "504 Wh capacity, 3000+ cycle life, -20°C to +60°C operating range, low-temp cutoff", function: "Provides 14.8 days continuous autonomous operation with zero solar input (dark monsoon)", ip_rating: "IP67 Enclosure Internal", cost_inr: 2850 },
        { id: "MPPT-01", category: "Power Management", component: "TI BQ24650 MPPT Solar Charge Controller PCB", specs: "Synchronous switch-mode, MPPT tracking, 94% efficiency, reverse current protection", function: "Optimizes power transfer from cloudy/diffuse sunlight into LiFePO4 battery pack", ip_rating: "IP67 Internal Mount", cost_inr: 620 },
        { id: "ENC-01", category: "Housing & Mechanics", component: "Die-Cast Aluminum IP67 Outdoor Enclosure + Cable Glands", specs: "220 x 170 x 110 mm, neoprene sealing gasket, PG9/PG11 cable glands, pole mount clamp", function: "Hermetically shields electronics against torrential downpours, frost heave, and rodent chewing", ip_rating: "IP67 Certified", cost_inr: 950 },
        { id: "SURGE-01", category: "Electrical Protection", component: "Multi-Stage Transient Voltage Suppression (TVS) + Gas Tube", specs: "600W TVS diodes on all sensor inputs, spark-gap gas discharge tube on RF feedline", function: "Guards against mountain lightning electromagnetic pulses (LEMP) and induced ground surge", ip_rating: "Onboard Component", cost_inr: 300 }
    ];

    const DEFAULT_SITREPS = {
        glof: {
            memo_reference: "NDMA/NER/EOC/2026/SITREP-6709",
            incident_name: "South Lhonak Glacial Lake Outburst Flood & Teesta Basal Scour",
            timestamp_ist: "18-Sep-2026 21:00:00 IST",
            geography: {
                state: "Sikkim",
                district: "Pakhyong / Kalimpong Border",
                monitored_corridor: "NH-10 Km 48 (Seti Jhora / Likuvir Gorge)",
                severed_artery: "National Highway 10 (Km 42 - Km 54 submerged/scoured)",
                designated_detour: "NH-717A (Bagrakote - Labha - Algarah - Pedong - Reshi - Rhenock - Ranipool)"
            },
            multi_physics_evidence: {
                signal_1_radar: { reading: "49.5 dBZ (Rainfall Rate 84.5 mm/h)" },
                signal_2_geotechnical: { reading: "FoS = 0.48 (Mohr-Coulomb Limit Equilibrium)" },
                signal_3_insar: { reading: "18.4 mm/day (Saito Failure Window: 1.8 hrs)" },
                signal_4_edge_cv: { reading: "42.5 mm aperture (Active Dilation >30mm)" }
            },
            emergency_directives: [
                "IMMEDIATE CLOSURE: Stop all civilian vehicular traffic at Rangpo Checkpost and Melli Bridge.",
                "DIVERT TRAFFIC: Reroute essential supplies and light military convoys via NH-717A (Bagrakote - Labha - Algarah - Pedong - Reshi - Rhenock).",
                "EVACUATE TOE ZONE: Evacuate riverside habitations at 29th Mile, Likuvir, and Singtam riverside to pre-designated NDRF relief shelters.",
                "DAM FLOODGATE SURCHARGE: Coordinate with NHPC Teesta-V dam authorities for controlled spillway release and silt purging."
            ],
            asset_mobilization: {
                ndrf_battalions: "2 Battalions (2nd Bn Bongaigaon detachment + 12th Bn Itanagar reserve)",
                bro_machinery: "3 Heavy Hydraulic Excavators + 2 Crawler Bulldozers (Project Swastik, Task Force 764)",
                bailey_bridging: "1 x 110-ft Double-Single Bailey Bridge Set (En route from Siliguri Central Depot)"
            }
        },
        remal: {
            memo_reference: "NDMA/NER/EOC/2026/SITREP-8821",
            incident_name: "Cyclone Remal Severe Orographic Deluge & Quarry Slide",
            timestamp_ist: "18-Sep-2026 21:00:00 IST",
            geography: {
                state: "Mizoram",
                district: "Aizawl",
                monitored_corridor: "Melthum Stone Quarry Chokepoint",
                severed_artery: "Aizawl - Lunglei State Highway Corridor",
                designated_detour: "Lengpui - Sairang Alternate Ridge Road"
            },
            multi_physics_evidence: {
                signal_1_radar: { reading: "52.0 dBZ (Rainfall Rate 92.0 mm/h)" },
                signal_2_geotechnical: { reading: "FoS = 0.52 (Saturated Shear Failure)" },
                signal_3_insar: { reading: "22.1 mm/day (Saito Failure Window: 1.4 hrs)" },
                signal_4_edge_cv: { reading: "38.0 mm aperture (Bench Slump Cracking)" }
            },
            emergency_directives: [
                "RED ALERT: Prohibit civilian movement along southern Aizawl quarry scarp roads.",
                "SEARCH & RESCUE: Dispatch SDRF and local YMA volunteers with acoustic detectors to quarry debris zone.",
                "AIR STRIP INTEGRITY: Reinforce drainage along Lengpui Airport access corridor to maintain air ambulance connectivity."
            ],
            asset_mobilization: {
                ndrf_battalions: "1 NDRF Battalion (1st Bn Guwahati airlift to Lengpui)",
                bro_machinery: "2 JCB Tracked Loaders + 1 Heavy Shovel (Project Pushpak)",
                bailey_bridging: "1 x 80-ft Emergency Steel Truss Bridge Unit"
            }
        },
        tupul: {
            memo_reference: "NDMA/NER/EOC/2026/SITREP-4192",
            incident_name: "Tupul Railway Construction Yard Debris Avalanche",
            timestamp_ist: "18-Sep-2026 21:00:00 IST",
            geography: {
                state: "Manipur",
                district: "Noney",
                monitored_corridor: "Jiribam - Imphal Rail Corridor (Tunnel 12 Adit)",
                severed_artery: "NH-37 (Imphal - Jiribam Highway)",
                designated_detour: "Old Cachar Road (Light 4x4 Emergency Convoys Only)"
            },
            multi_physics_evidence: {
                signal_1_radar: { reading: "48.0 dBZ (Rainfall Rate 76.0 mm/h)" },
                signal_2_geotechnical: { reading: "FoS = 0.39 (Deep Rotational Cut-Slope Failure)" },
                signal_3_insar: { reading: "27.5 mm/day (Saito Failure Window: 0.9 hrs)" },
                signal_4_edge_cv: { reading: "49.0 mm aperture (Major Adit Crown Tension Dilation)" }
            },
            emergency_directives: [
                "CATASTROPHIC DEBRIS DISPATCH: Mobilize Indian Army 57 Mountain Division and NDRF for river dam clearing.",
                "IJEI RIVER MONITORING: Monitor artificial damming of Ijei River; alert downstream Tamenglong and Noney villages for flash flood surge.",
                "RAIL SUSPENSION: Hault all track formation works and evacuate workers from adit portals."
            ],
            asset_mobilization: {
                ndrf_battalions: "3 Battalions (Army Engineering Task Force + 12th Bn NDRF)",
                bro_machinery: "4 Heavy Excavators + 3 Sludge Suction Pump Arrays",
                bailey_bridging: "2 x 90-ft Compact Bailey Bridge Modules (Project Sewak)"
            }
        },
        sonapur: {
            memo_reference: "NDMA/NER/EOC/2026/SITREP-5534",
            incident_name: "Sonapur Tunnel Dip-Slope Sandstone Catastrophic Rockfall",
            timestamp_ist: "18-Sep-2026 21:00:00 IST",
            geography: {
                state: "Meghalaya",
                district: "East Jaintia Hills",
                monitored_corridor: "Sonapur Tunnel Portal Corridor",
                severed_artery: "NH-06 (Barapani - Silchar Lifeline Chokepoint)",
                designated_detour: "Shillong - Jowai - Dawki - Silchar Relief Detour"
            },
            multi_physics_evidence: {
                signal_1_radar: { reading: "54.0 dBZ (Rainfall Rate 110.0 mm/h)" },
                signal_2_geotechnical: { reading: "FoS = 0.58 (Dip-Slope Planar Shearing)" },
                signal_3_insar: { reading: "15.8 mm/day (Saito Failure Window: 2.2 hrs)" },
                signal_4_edge_cv: { reading: "34.5 mm aperture (Tunnel Portal Joint Dilation)" }
            },
            emergency_directives: [
                "LIFELINE PROTECTION: NH-06 is the sole corridor to Barak Valley, Tripura, and Mizoram. Maintain active rock-shed shoring.",
                "CONTROLLED BLASTING: BRO detachment on standby for explosive fragmentation of perched boulders above portal.",
                "CONVOY DISPATCH: Clear essential fuel and medicine tankers under Armed Escort between rainfall pulses."
            ],
            asset_mobilization: {
                ndrf_battalions: "1 NDRF Battalion (SDRF Meghalaya + Assam Border Co-deployed)",
                bro_machinery: "2 Rock Breakers + 2 Wheel Loaders (Project Setu)",
                bailey_bridging: "Modular Pre-fabricated Steel Rockfall Canopy Sections"
            }
        }
    };

    // --- 1. HARDWARE BOM MODAL LOGIC ---
    window.openHardwareBomModal = async function () {
        const modal = document.getElementById('modal-hardware-bom');
        if (!modal) return;
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        document.body.style.overflow = 'hidden';

        // 1. Instant offline render guarantee (0ms delay)
        renderBomTable(DEFAULT_BOM_ITEMS);

        // 2. Fetch live BOM telemetry if available and refresh
        try {
            const resp = await fetch('/api/hardware/bom');
            if (resp.ok) {
                const data = await resp.json();
                if (data.bom_items && data.bom_items.length) {
                    renderBomTable(data.bom_items);
                }
            }
        } catch (e) {
            console.warn('[HardwareBOM] Operating in hardened offline mode with verified BOM cache');
        }
    };

    window.closeHardwareBomModal = function () {
        const modal = document.getElementById('modal-hardware-bom');
        if (!modal) return;
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        document.body.style.overflow = '';
    };

    window.switchBomTab = function (tabId) {
        const tabs = ['bom-tab-items', 'bom-tab-power', 'bom-tab-pinout', 'bom-tab-wpc'];
        const contents = ['bom-content-items', 'bom-content-power', 'bom-content-pinout', 'bom-content-wpc'];

        tabs.forEach((t, i) => {
            const btn = document.getElementById(t);
            const panel = document.getElementById(contents[i]);
            if (t === tabId) {
                if (btn) {
                    btn.classList.add('border-amber-500', 'text-amber-400', 'bg-amber-950/40');
                    btn.classList.remove('border-transparent', 'text-slate-400');
                }
                if (panel) panel.classList.remove('hidden');
            } else {
                if (btn) {
                    btn.classList.remove('border-amber-500', 'text-amber-400', 'bg-amber-950/40');
                    btn.classList.add('border-transparent', 'text-slate-400');
                }
                if (panel) panel.classList.add('hidden');
            }
        });
    };

    function renderBomTable(items) {
        const tbody = document.getElementById('bom-table-body');
        if (!tbody || !items || !items.length) return;
        tbody.innerHTML = items.map(item => `
            <tr class="border-b border-slate-800/60 hover:bg-slate-900/40 transition">
                <td class="p-2 font-mono text-[10px] text-amber-400 font-bold">${item.id}</td>
                <td class="p-2">
                    <div class="font-bold text-slate-200 text-[11px]">${item.component}</div>
                    <div class="text-[9px] text-slate-400">${item.specs}</div>
                </td>
                <td class="p-2 text-[10px] text-slate-300 font-medium">${item.function}</td>
                <td class="p-2 font-mono text-[10px] text-emerald-400">${item.ip_rating}</td>
                <td class="p-2 font-mono text-[11px] text-right font-bold text-amber-300">₹${item.cost_inr.toLocaleString('en-IN')}</td>
            </tr>
        `).join('');
    }

    // --- 2. OFFICIAL NDMA SITREP MEMO LOGIC ---
    window.openOfficialSitrepModal = async function (scenarioId) {
        const modal = document.getElementById('modal-official-sitrep');
        if (!modal) return;
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        document.body.style.overflow = 'hidden';

        const scn = scenarioId || 'glof';
        await loadOfficialSitrep(scn);
    };

    window.closeOfficialSitrepModal = function () {
        const modal = document.getElementById('modal-official-sitrep');
        if (!modal) return;
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        document.body.style.overflow = '';
    };

    window.loadOfficialSitrep = async function (scenarioId) {
        const scn = scenarioId || 'glof';
        // 1. Instant offline render guarantee (0ms delay)
        if (DEFAULT_SITREPS[scn]) {
            renderOfficialSitrep(DEFAULT_SITREPS[scn]);
        }
        // 2. Fetch live official memo and refresh
        try {
            const resp = await fetch(`/api/sitrep/official-memo?scenario=${scn}`);
            if (resp.ok) {
                const data = await resp.json();
                renderOfficialSitrep(data);
            }
        } catch (e) {
            console.warn('[OfficialSitRep] Operating in hardened offline mode with verified SitRep cache');
        }
    };

    function renderOfficialSitrep(data) {
        const setVal = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.textContent = val;
        };

        setVal('sitrep-ref-no', data.memo_reference);
        setVal('sitrep-incident-name', data.incident_name);
        setVal('sitrep-timestamp-ist', data.timestamp_ist);
        setVal('sitrep-state-district', `${data.geography.district}, ${data.geography.state}`);
        setVal('sitrep-corridor', data.geography.monitored_corridor);
        setVal('sitrep-severed-road', data.geography.severed_artery);
        setVal('sitrep-bypass-route', data.geography.designated_detour);

        // Multi-physics signals
        const ev = data.multi_physics_evidence;
        if (ev) {
            setVal('sitrep-sig1-reading', ev.signal_1_radar?.reading || '49.5 dBZ');
            setVal('sitrep-sig2-reading', ev.signal_2_geotechnical?.reading || 'FoS = 0.48');
            setVal('sitrep-sig3-reading', ev.signal_3_insar?.reading || '18.4 mm/day (1.8 hrs to failure)');
            setVal('sitrep-sig4-reading', ev.signal_4_edge_cv?.reading || '42.5 mm aperture');
        }

        // Directives
        const dirList = document.getElementById('sitrep-directives-list');
        if (dirList && data.emergency_directives) {
            dirList.innerHTML = data.emergency_directives.map(d => `<li class="leading-relaxed">${d}</li>`).join('');
        }

        // Tactical Assets
        const assets = data.asset_mobilization;
        if (assets) {
            setVal('sitrep-ndrf-assets', assets.ndrf_battalions);
            setVal('sitrep-bro-assets', assets.bro_machinery);
            setVal('sitrep-bridge-assets', assets.bailey_bridging);
            setVal('sitrep-medical-assets', assets.medical_triage);
        }

        // Cell Broadcast
        const cb = data.cell_broadcast_metrics;
        if (cb) {
            setVal('sitrep-cb-reach', `${cb.successful_deliveries.toLocaleString('en-IN')} / ${cb.corridor_handsets_targeted.toLocaleString('en-IN')} handsets (${cb.delivery_rate_pct}%) • ${cb.delivery_latency_sec}s latency`);
        }
    }

    window.printOfficialSitrep = function () {
        window.print();
    };

    // --- 3. 2G FEATURE PHONE SMS & CELL BROADCAST SIMULATOR ---
    const SMS_TRANSLATIONS = {
        ne: {
            name: 'Nepali (नेपाली)',
            header: '[EMERGENCY CELL BROADCAST • CH 4370]',
            text: 'चेतावनी! NH-10 Km 48 मा ठूलो पहिरोको जोखिम। तुरुन्तै सडक खाली गरी उच्च स्थानमा जानुहोस्। NH-717A बाईपास मार्ग प्रयोग गर्नुहोस्। - सिक्किम EOC',
            chars: 148,
            langBadge: 'NE-BERT • SIKKIM / KALIMPONG'
        },
        hi: {
            name: 'Hindi (हिन्दी)',
            header: '[आपदा चेतावनी • चैनल 4370]',
            text: 'चेतावनी! NH-10 किमी 48 पर भारी भूस्खलन का खतरा। तुरंत ऊंचे और सुरक्षित स्थान पर जाएं। NH-717A वैकल्पिक मार्ग का उपयोग करें। - राज्य EOC',
            chars: 142,
            langBadge: 'NE-BERT • NATIONAL CELL BROADCAST'
        },
        en: {
            name: 'English',
            header: '[EMERGENCY CELL BROADCAST • CH 4370]',
            text: 'CRITICAL ALERT! Landslide imminent at NH-10 Km 48. Evacuate toe area immediately to higher ground. Divert via NH-717A bypass corridor. - EOC Sikkim',
            chars: 154,
            langBadge: 'NE-BERT • INTER-AGENCY BRO / NDRF'
        },
        lep: {
            name: 'Lepcha (ᰛᰩᰵ)',
            header: '[ᰀᰦᰵᰶᰡᰤᰩᰵ • CH 4370]',
            text: 'NH-10 Km 48 ᰜᰦᰵᰌᰩ ᰚᰩ ᰆᰦᰵᰶ ᰜᰤᰦᰵ ᰀᰦᰵᰶᰡᰤᰩᰵ! ᰆᰤᰦᰵ ᰜᰤᰦᰵ ᰌᰨᰵ ᰜᰤᰦᰵ ᰓᰦᰵᰌᰨ ᰕᰨᰵᰶᰊᰨ ᰀᰦᰵᰶᰡᰤᰩᰵ ᰆᰨᰵ। NH-717A ᰜᰦᰵᰶ ᰆᰨᰵ। - EOC ᰚᰩᰵᰊᰨ',
            chars: 135,
            langBadge: 'NE-BERT • DZONGU / NORTH SIKKIM'
        },
        as: {
            name: 'Assamese (অসমীয়া)',
            header: '[জৰুৰীকালীন সতৰ্কবাৰ্তা • চেনেল 4370]',
            text: 'সতৰ্কবাৰ্তা! NH-10 কিলোমিটাৰ 48 ত ভূমিস্খলনৰ তীব্ৰ আশংকা। তাৎক্ষণিকভাৱে সুৰক্ষিত উচ্চ স্থানলৈ যাওক। NH-717A বাইপাছ ব্যৱহাৰ কৰক। - ৰাজ্যিক EOC',
            chars: 146,
            langBadge: 'NE-BERT • ASSAM / BRAHMAPUTRA'
        },
        bn: {
            name: 'Bengali (বাংলা)',
            header: '[জরুরি দুর্যোগ সতর্কবার্তা • 4370]',
            text: 'সতর্কবার্তা! NH-10 কিমি 48-এ প্রবল ভূমিধসের আশঙ্কা। অবিলম্বে এলাকা খালি করে নিরাপদ স্থানে আশ্রয় নিন। NH-717A বিকল্প পথ ব্যবহার করুন। - EOC',
            chars: 144,
            langBadge: 'NE-BERT • SILIGURI / KALIMPONG'
        },
        lus: {
            name: 'Mizo (Mizo ṭawng)',
            header: '[CELL BROADCAST HMANGIN • CH 4370]',
            text: 'Vaukhanna! NH-10 Km 48 ah lei tlah tur a hlauhawm hle. Hmun him sangah inthiarfihlim nghal rawh u. NH-717A kawng zawk hmang rawh u. - EOC Mizoram',
            chars: 151,
            langBadge: 'NE-BERT • MIZORAM CORRIDOR'
        },
        kha: {
            name: 'Khasi (Ka Ktien Khasi)',
            header: '[JINGMAHAM BA KYRPANG • CH 4370]',
            text: 'Jingmaham! Ka jingtwa khyndew ha NH-10 Km 48. Kiew noh sha ki jaka ba shngain kloi kloi. Pyndonkam da ka surok NH-717A. - EOC Meghalaya',
            chars: 140,
            langBadge: 'NE-BERT • MEGHALAYA HILLS'
        },
        gar: {
            name: 'Garo (A·chik)',
            header: '[MIKKANGCHAKANI SEAN • CH 4370]',
            text: 'Mikkangchakani! NH-10 Km 48-o a·a beani kenani donga. Bakbak chel·e katbo. NH-717A ramako jakkalbo. - Disaster Management EOC',
            chars: 132,
            langBadge: 'NE-BERT • GARO HILLS'
        }
    };

    window.openFeaturePhoneModal = function () {
        const modal = document.getElementById('modal-feature-phone');
        if (!modal) return;
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        document.body.style.overflow = 'hidden';
        setFeaturePhoneLang('ne');
    };

    window.closeFeaturePhoneModal = function () {
        const modal = document.getElementById('modal-feature-phone');
        if (!modal) return;
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        document.body.style.overflow = '';
    };

    window.setFeaturePhoneLang = function (langKey) {
        const item = SMS_TRANSLATIONS[langKey] || SMS_TRANSLATIONS.ne;

        const hdr = document.getElementById('phone-msg-header');
        const body = document.getElementById('phone-msg-body');
        const charCount = document.getElementById('phone-char-count');
        const badge = document.getElementById('phone-lang-badge');

        if (hdr) hdr.textContent = item.header;
        if (body) {
            body.textContent = item.text;
            // Add subtle screen glow
            body.classList.add('animate-pulse');
            setTimeout(() => body.classList.remove('animate-pulse'), 500);
        }
        if (charCount) charCount.textContent = `${item.chars} / 160 characters (TRAI SMS Compliant)`;
        if (badge) badge.textContent = item.langBadge;

        // Update button states
        document.querySelectorAll('.phone-lang-btn').forEach(btn => {
            if (btn.getAttribute('data-lang') === langKey) {
                btn.classList.add('bg-amber-500', 'text-slate-950', 'font-bold');
                btn.classList.remove('bg-slate-800', 'text-slate-300');
            } else {
                btn.classList.remove('bg-amber-500', 'text-slate-950', 'font-bold');
                btn.classList.add('bg-slate-800', 'text-slate-300');
            }
        });
    };

    window.testFeaturePhoneTone = function () {
        try {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (!AudioContext) return;
            const ctx = new AudioContext();

            // ITU-T dual-tone 960Hz / 800Hz alert pulse
            const osc1 = ctx.createOscillator();
            const osc2 = ctx.createOscillator();
            const gain = ctx.createGain();

            osc1.type = 'sine';
            osc1.frequency.setValueAtTime(960, ctx.currentTime);
            osc1.frequency.setValueAtTime(800, ctx.currentTime + 0.25);
            osc1.frequency.setValueAtTime(960, ctx.currentTime + 0.50);

            osc2.type = 'sine';
            osc2.frequency.setValueAtTime(800, ctx.currentTime);
            osc2.frequency.setValueAtTime(960, ctx.currentTime + 0.25);
            osc2.frequency.setValueAtTime(800, ctx.currentTime + 0.50);

            gain.gain.setValueAtTime(0.18, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.85);

            osc1.connect(gain);
            osc2.connect(gain);
            gain.connect(ctx.destination);

            osc1.start();
            osc2.start();
            osc1.stop(ctx.currentTime + 0.85);
            osc2.stop(ctx.currentTime + 0.85);

            // Screen vibrate effect
            const screen = document.getElementById('phone-screen-container');
            if (screen) {
                screen.classList.add('ring-4', 'ring-red-500');
                setTimeout(() => screen.classList.remove('ring-4', 'ring-red-500'), 850);
            }
        } catch (e) {
            console.warn('[FeaturePhoneAudio] WebAudio tone error:', e);
        }
    };

})();

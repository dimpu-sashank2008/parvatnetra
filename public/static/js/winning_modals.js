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

    // --- 1. HARDWARE BOM MODAL LOGIC ---
    window.openHardwareBomModal = async function () {
        const modal = document.getElementById('modal-hardware-bom');
        if (!modal) return;
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        document.body.style.overflow = 'hidden';

        // Fetch live BOM telemetry if available
        try {
            const resp = await fetch('/api/hardware/bom');
            if (resp.ok) {
                const data = await resp.json();
                renderBomTable(data.bom_items);
            }
        } catch (e) {
            console.warn('[HardwareBOM] Using preloaded telemetry:', e);
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
        try {
            const resp = await fetch(`/api/sitrep/official-memo?scenario=${scenarioId}`);
            if (resp.ok) {
                const data = await resp.json();
                renderOfficialSitrep(data);
            }
        } catch (e) {
            console.error('[OfficialSitRep] Fetch error:', e);
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

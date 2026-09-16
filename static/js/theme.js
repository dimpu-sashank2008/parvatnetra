/**
 * PARVAT NETRA / PAHAD AI — Unified Theme Management Engine
 * Provides persistent Light Mode (Faded Saffron) & Dark Mode (Obsidian & Faded Blue)
 * synchronization across all portal routes and dashboards.
 */

(function () {
    'use strict';

    function getSavedTheme() {
        try {
            return localStorage.getItem('parvat_theme') || 'dark';
        } catch (e) {
            return 'dark';
        }
    }

    function applyTheme(theme) {
        var isLight = (theme === 'light');
        var root = document.documentElement;
        var body = document.body;

        if (isLight) {
            root.classList.remove('dark');
            root.classList.add('light');
            if (body) {
                body.classList.remove('dark-mode');
                body.classList.add('light-mode');
            }
        } else {
            root.classList.add('dark');
            root.classList.remove('light');
            if (body) {
                body.classList.add('dark-mode');
                body.classList.remove('light-mode');
            }
        }

        updateThemeUI(isLight);

        // Dispatch custom event for 3D canvases, Leaflet tiles, and charts
        try {
            window.dispatchEvent(new CustomEvent('parvat-theme-changed', {
                detail: { theme: theme, isLight: isLight }
            }));
        } catch (err) {}
    }

    function updateThemeUI(isLight) {
        var icon = document.getElementById('theme-icon');
        var text = document.getElementById('theme-text');
        var btn = document.getElementById('theme-toggle-btn');

        if (icon) {
            icon.innerHTML = isLight
                ? '<i class="ph-bold ph-moon text-sky-500 text-xs" aria-hidden="true"></i>'
                : '<i class="ph-bold ph-sun text-amber-400 text-xs" aria-hidden="true"></i>';
        }

        if (text) {
            text.innerText = isLight ? 'Dark Mode' : 'Light Mode';
        }

        if (btn) {
            btn.className = isLight
                ? 'px-2.5 py-1 bg-white border border-amber-200 rounded text-slate-700 hover:bg-amber-50 hover:text-amber-900 transition flex items-center gap-1.5 text-xs font-semibold shadow-xs active:scale-95 cursor-pointer'
                : 'px-2.5 py-1 bg-[#12213D] border border-blue-300/30 rounded text-sky-100 hover:bg-[#1A3158] hover:text-white transition flex items-center gap-1.5 text-xs font-semibold shadow-xs active:scale-95 cursor-pointer';
            btn.title = isLight ? 'Switch to Dark Mode (Obsidian & Blue)' : 'Switch to Light Mode (Faded Saffron)';
            btn.setAttribute('aria-label', btn.title);
        }
    }

    function toggleTheme() {
        var current = getSavedTheme();
        var next = (current === 'light') ? 'dark' : 'light';
        try {
            localStorage.setItem('parvat_theme', next);
        } catch (e) {}
        applyTheme(next);

        if (typeof window.showToast === 'function') {
            window.showToast(
                next === 'light' ? 'Switched to Government Standard Light Theme' : 'Switched to Tactical EOC Dark Theme',
                'info'
            );
        }
    }

    function initTheme() {
        var theme = getSavedTheme();
        applyTheme(theme);
    }

    // Expose global methods
    window.toggleTheme = toggleTheme;
    window.initTheme = initTheme;
    window.updateThemeUI = updateThemeUI;
    window.toggleObservatoryTheme = toggleTheme;
    window.initObservatoryTheme = initTheme;

    // Apply immediately to prevent FOUC
    var immediateTheme = getSavedTheme();
    if (immediateTheme === 'light') {
        document.documentElement.classList.add('light');
        document.documentElement.classList.remove('dark');
    } else {
        document.documentElement.classList.add('dark');
        document.documentElement.classList.remove('light');
    }

    if (document.body) {
        if (immediateTheme === 'light') {
            document.body.classList.add('light-mode');
            document.body.classList.remove('dark-mode');
        } else {
            document.body.classList.add('dark-mode');
            document.body.classList.remove('light-mode');
        }
    }

    // Listen for DOM ready to bind elements
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            initTheme();
        });
    } else {
        initTheme();
    }

    // Cross-tab sync via storage event
    window.addEventListener('storage', function (e) {
        if (e.key === 'parvat_theme') {
            applyTheme(e.newValue || 'dark');
        }
    });
})();

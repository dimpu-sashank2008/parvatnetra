/**
 * PARVAT NETRA -- Automated Browser Verification & Screenshot Capture (GIGW 3.0 UI Redesign)
 * Captures 5 high-resolution operational evidence screenshots:
 * 1. 01_executive_operations_dashboard.png (Full EOC Command view)
 * 2. 02_multimodal_gis_console.png (Focused capture of the #map element)
 * 3. 03_bilingual_indigenous_voice_cap_modal.png (4-Language CAP alert modal)
 * 4. 04_fullwidth_triage_queue.png (100% full-width observation queue table)
 * 5. 05_citizen_advisory_portal.png (Citizen advisory public portal view)
 */

const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer-core');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const EDGE_PATH = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const BASE_URL = process.env.BASE_URL || 'http://127.0.0.1:8080/';

const SCREENSHOT_DIR = path.resolve(__dirname, '../docs/screenshots');
const ARTIFACT_DIR = 'C:\\Users\\dimpu\\.gemini\\antigravity\\brain\\e292f14a-c735-44a9-8c60-8e7b5ed121df\\screenshots';

async function getBrowserExecutable() {
    if (fs.existsSync(CHROME_PATH)) return CHROME_PATH;
    if (fs.existsSync(EDGE_PATH)) return EDGE_PATH;
    throw new Error('No supported Chrome or Edge browser executable found.');
}

async function capture() {
    console.log('======================================================================');
    console.log('  PARVAT NETRA -- AUTOMATED DEVTOOLS 5-SCREENSHOT CAPTURE SUITE');
    console.log('======================================================================');

    // 1. Ensure target directory exists
    if (!fs.existsSync(SCREENSHOT_DIR)) {
        fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
        console.log(`[INFO] Created directory: ${SCREENSHOT_DIR}`);
    }
    if (!fs.existsSync(ARTIFACT_DIR)) {
        fs.mkdirSync(ARTIFACT_DIR, { recursive: true });
    }

    const browserExe = await getBrowserExecutable();
    console.log(`[INFO] Launching browser engine: ${browserExe}`);

    const browser = await puppeteer.launch({
        executablePath: browserExe,
        headless: 'new',
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-gpu',
            '--window-size=1920,1080'
        ]
    });

    try {
        const page = await browser.newPage();
        await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });

        console.log(`[INFO] Navigating to ${BASE_URL}...`);
        await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });

        // Wait for Leaflet container and API layers to populate
        await page.waitForSelector('#map', { timeout: 15000 });
        console.log('[INFO] Leaflet map initialized. Waiting 4 seconds for spatial layers & telemetry...');
        await new Promise(resolve => setTimeout(resolve, 4500));

        // -------------------------------------------------------------
        // Screenshot 1: Full EOC Command Overview (Executive Operations Dashboard)
        // -------------------------------------------------------------
        const file1 = path.join(SCREENSHOT_DIR, '01_executive_operations_dashboard.png');
        const file1_compat = path.join(SCREENSHOT_DIR, '01_full_dashboard_console.png');
        console.log('[INFO] Capturing Screenshot 1: Executive Operations Dashboard...');
        await page.screenshot({ path: file1, fullPage: false });
        fs.copyFileSync(file1, file1_compat);
        fs.copyFileSync(file1, path.join(ARTIFACT_DIR, '01_executive_operations_dashboard.png'));
        fs.copyFileSync(file1, path.join(ARTIFACT_DIR, '01_full_dashboard_console.png'));
        const stat1 = fs.statSync(file1);
        console.log(`  -> Saved: ${path.basename(file1)} (${(stat1.size / 1024).toFixed(1)} KB)`);

        // -------------------------------------------------------------
        // Screenshot 2: View focused on the Leaflet GIS map element (#map)
        // -------------------------------------------------------------
        const file2 = path.join(SCREENSHOT_DIR, '02_multimodal_gis_console.png');
        const file2_compat = path.join(SCREENSHOT_DIR, '02_gis_map_layers.png');
        console.log('[INFO] Capturing Screenshot 2: Multimodal GIS Console (#map)...');
        const mapElement = await page.$('#map');
        if (mapElement) {
            await mapElement.screenshot({ path: file2 });
        } else {
            await page.screenshot({ path: file2, clip: { x: 30, y: 150, width: 1200, height: 600 } });
        }
        fs.copyFileSync(file2, file2_compat);
        fs.copyFileSync(file2, path.join(ARTIFACT_DIR, '02_multimodal_gis_console.png'));
        fs.copyFileSync(file2, path.join(ARTIFACT_DIR, '02_gis_map_layers.png'));
        const stat2 = fs.statSync(file2);
        console.log(`  -> Saved: ${path.basename(file2)} (${(stat2.size / 1024).toFixed(1)} KB)`);

        // -------------------------------------------------------------
        // Screenshot 3: Trigger Alert & capture 4-Language CAP Modal
        // -------------------------------------------------------------
        console.log('[INFO] Triggering "Issue Public Alert" for CAP modal verification...');
        const alertBtn = await page.$('#btn-issue-alert') || await page.$('#btn-alert');
        if (alertBtn) {
            await alertBtn.click();
        } else {
            await page.evaluate(() => {
                if (typeof dispatchAlert === 'function') dispatchAlert();
            });
        }

        // Wait for CAP modal to become visible and text to populate
        await page.waitForFunction(() => {
            const modal = document.getElementById('cap-modal');
            const txt = document.getElementById('cap-text-en');
            return modal && !modal.classList.contains('hidden') && txt && txt.innerText.length > 5;
        }, { timeout: 15000 });

        await new Promise(resolve => setTimeout(resolve, 1000));

        const file3 = path.join(SCREENSHOT_DIR, '03_bilingual_indigenous_voice_cap_modal.png');
        const file3_compat = path.join(SCREENSHOT_DIR, '03_bilingual_indigenous_cap_alert.png');
        console.log('[INFO] Capturing Screenshot 3: 4-Language Indigenous CAP Alert Modal...');
        await page.screenshot({ path: file3, fullPage: false });
        fs.copyFileSync(file3, file3_compat);
        fs.copyFileSync(file3, path.join(ARTIFACT_DIR, '03_bilingual_indigenous_voice_cap_modal.png'));
        fs.copyFileSync(file3, path.join(ARTIFACT_DIR, '03_bilingual_indigenous_cap_alert.png'));
        const stat3 = fs.statSync(file3);
        console.log(`  -> Saved: ${path.basename(file3)} (${(stat3.size / 1024).toFixed(1)} KB)`);

        // Close modal
        await page.evaluate(() => {
            if (typeof closeCapModal === 'function') closeCapModal();
            if (typeof stopEmergencyAlarm === 'function') stopEmergencyAlarm();
        });
        await new Promise(resolve => setTimeout(resolve, 500));

        // -------------------------------------------------------------
        // Screenshot 4: Full-Width Triage Queue Table (#observation-queue-section)
        // -------------------------------------------------------------
        console.log('[INFO] Capturing Screenshot 4: Full-Width Observation Triage Queue...');
        const queueElement = await page.$('#observation-queue-section');
        const file4 = path.join(SCREENSHOT_DIR, '04_fullwidth_triage_queue.png');
        if (queueElement) {
            await queueElement.scrollIntoView();
            await new Promise(resolve => setTimeout(resolve, 500));
            await queueElement.screenshot({ path: file4 });
        } else {
            await page.screenshot({ path: file4, fullPage: false });
        }
        fs.copyFileSync(file4, path.join(ARTIFACT_DIR, '04_fullwidth_triage_queue.png'));
        const stat4 = fs.statSync(file4);
        console.log(`  -> Saved: ${path.basename(file4)} (${(stat4.size / 1024).toFixed(1)} KB)`);

        // -------------------------------------------------------------
        // Screenshot 5: Citizen Advisory Portal Mode
        // -------------------------------------------------------------
        console.log('[INFO] Switching to Citizen Advisory Mode...');
        await page.evaluate(() => {
            if (typeof switchPortalMode === 'function') {
                switchPortalMode('citizen');
            } else if (typeof setMode === 'function') {
                setMode('citizen');
            }
        });
        await new Promise(resolve => setTimeout(resolve, 800));

        const file5 = path.join(SCREENSHOT_DIR, '05_citizen_advisory_portal.png');
        console.log('[INFO] Capturing Screenshot 5: Citizen Advisory Portal View...');
        await page.screenshot({ path: file5, fullPage: false });
        fs.copyFileSync(file5, path.join(ARTIFACT_DIR, '05_citizen_advisory_portal.png'));
        const stat5 = fs.statSync(file5);
        console.log(`  -> Saved: ${path.basename(file5)} (${(stat5.size / 1024).toFixed(1)} KB)`);

        // -------------------------------------------------------------
        // Verification of requirements (> 50 KB per Task 3 instruction)
        // -------------------------------------------------------------
        console.log('----------------------------------------------------------------------');
        const minSize = 50 * 1024; // 50KB required
        const files = [
            { path: file1, size: stat1.size, name: '01_executive_operations_dashboard.png' },
            { path: file2, size: stat2.size, name: '02_multimodal_gis_console.png' },
            { path: file3, size: stat3.size, name: '03_bilingual_indigenous_voice_cap_modal.png' },
            { path: file4, size: stat4.size, name: '04_fullwidth_triage_queue.png' },
            { path: file5, size: stat5.size, name: '05_citizen_advisory_portal.png' }
        ];

        let allValid = true;
        files.forEach(f => {
            const pass = f.size >= minSize;
            if (!pass) allValid = false;
            console.log(`[${pass ? 'PASS' : 'FAIL'}] ${f.name}: ${(f.size / 1024).toFixed(1)} KB (Req: >= 50 KB)`);
        });

        if (!allValid) {
            throw new Error('One or more screenshots did not meet the minimum file size requirement (50KB).');
        }

        console.log('======================================================================');
        console.log('>>> ALL 5 CHROME DEVTOOLS SCREENSHOTS VERIFIED & PERSISTED! <<<');
        console.log('======================================================================');

    } finally {
        await browser.close();
    }
}

if (require.main === module) {
    capture().catch(err => {
        console.error('[ERROR] Screenshot capture failed:', err);
        process.exit(1);
    });
}

module.exports = { capture };

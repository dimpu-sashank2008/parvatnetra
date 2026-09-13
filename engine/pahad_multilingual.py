"""
engine/pahad_multilingual.py
============================
PAHAD Phase 3 — NE-BERT Multilingual Alert Synthesis Engine
------------------------------------------------------------
Synthesizes localized, culture-aware disaster warning payloads
across 9 North-Eastern Region (NER) languages and dialects, plus
English and Hindi national emergency communications baselines.

Languages Supported:
  1. Assamese       (as)   - Assam
  2. Khasi          (kha)  - Meghalaya (Khasi Hills)
  3. Garo           (grt)  - Meghalaya (Garo Hills)
  4. Meitei/Manipuri (mni) - Manipur
  5. Mizo           (lus)  - Mizoram
  6. Nyishi         (njz)  - Arunachal Pradesh
  7. Nagamese       (nag)  - Nagaland (lingua franca)
  8. Kokborok       (trp)  - Tripura
  9. Pnar           (pnar) - Meghalaya (Jaintia Hills)
  10. English       (en)   - National / Institutional
  11. Hindi         (hi)   - National / Official

Output Constraints:
- SMS character limit: strictly < 160 characters (TRAI / C-DOT standards)
- Rich Push Notifications: Headline, detailed advisory, detour directions
- Audio / Voice Synthesizer prompt text for public address sirens

Author : PARVAT NETRA / PAHAD Engineering Team
Data   : [SIMULATED] NE-BERT Multilingual Alert Synthesis v1
"""

from __future__ import annotations

from typing import Dict, Any, List

NER_DIALECT_CODES: List[str] = [
    "as", "kha", "grt", "mni", "lus", "njz", "nag", "trp", "pnar"
]

ALL_SUPPORTED_LANGUAGES: List[str] = NER_DIALECT_CODES + ["en", "hi"]

# Base template dictionary by language code
_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "as": {
        "language_name": "Assamese",
        "script": "Bengali-Assamese",
        "state": "Assam",
        "sms": "জৰুৰী সতৰ্কতা: {sec}ত ভূমিস্খলনৰ প্ৰচণ্ড আশংকা। {det}। সুৰক্ষিত স্থানলৈ যাওক।",
        "push_title": "[সতৰ্কবাণী] {sec}ত ভূমিস্খলনৰ সতৰ্কতা",
        "push_body": "{sec} পাহাৰীয়া এলেকাত ভূমিস্খলনৰ অতি উচ্চ আশংকা ধৰা পৰিছে। অনুগ্ৰহ কৰি তাৎক্ষণিকভাৱে সুৰক্ষিত আশ্ৰয়স্থললৈ যাওক। বিকল্প পথ: {det}।",
        "voice_script": "সকলোৰে দৃষ্টি আকৰ্ষণ কৰা হৈছে। {sec}ত ভূমিস্খলনৰ আশংকা আছে। বিকল্প পথ ব্যৱহাৰ কৰক।",
    },
    "kha": {
        "language_name": "Khasi",
        "script": "Latin",
        "state": "Meghalaya",
        "sms": "Jingpynbna Kyrkieh: Jingtwa khyndew ha {sec}. {det}. Kiew sha ki jaka ba heh mar-mar.",
        "push_title": "[JINGPYNBNA] Jingtwa Khyndew ha {sec}",
        "push_body": "Don ka jingshlei bad jingtwa khyndew kaba jur ha {sec}. Pynkynriah noh mar-mar sha ki jaka ba shngain. Lad ban leit: {det}.",
        "voice_script": "Sngewbha pynleit jingmut. Don ka jingtwa khyndew ha {sec}. Kiew sha ki jaka ba heh bad shngain.",
    },
    "grt": {
        "language_name": "Garo",
        "script": "Latin",
        "state": "Meghalaya",
        "sms": "Mikrakatani: {sec}o a·a beani a·sel gnang. {det}. Bakbak chel·ao katbo.",
        "push_title": "[MIKRAKATANI] A·a Beani {sec}",
        "push_body": "{sec} biapo a·a beani namen mongsonggipa a·sel gnang. Katangbo neng·takramona. Rama gipin: {det}.",
        "voice_script": "Ppilgipa manderang na·simang knatimbo. {sec}o a·a beani gnang. Bakbak safe biapona re·angbo.",
    },
    "mni": {
        "language_name": "Meitei / Manipuri",
        "script": "Meitei Mayek",
        "state": "Manipur",
        "sms": "অকুপ্পা পাউ: {sec}দা চীং থুগাইবগী অশোইবা লৈরে। {det}। কান্নবা মফমদা চৎলু।",
        "push_title": "[চেকশিনৱা] {sec}দা চীং থুগাইবগী পাউ",
        "push_body": "{sec}দা চীং থুগাইবগী অচৌবা খুদোংথিবা লৈরে। অথুবা মতমদা অশোই-অঙাম থোক্তবা মফমদা লৈবাক মীয়াম পুথোকউ। অমুক্তং চৎনবা লম্বী: {det}।",
        "voice_script": "মীয়ামগী পুকনিং চিংশিজরি। {sec}দা চীং থুগাইবগী অশোইবা লৈরে। অশোইবা লৈতবা মফমদা চৎলু।",
    },
    "lus": {
        "language_name": "Mizo",
        "script": "Latin",
        "state": "Mizoram",
        "sms": "Vauhkhan Thuthar: {sec}-ah leimin hlauhawm a awm. {det}. Hmun him lam pan nghal rawh.",
        "push_title": "[VAUHKHAN] Leimin Hlauhawm - {sec}",
        "push_body": "{sec} kawngpui bulah leimin hlauhawm tak a chhuak mek. Hmun him lam pan vat rawh u. Kawng dang: {det}.",
        "voice_script": "Khawngaihin lo ngaithla ula. {sec} ah leimin hlauhawm tak a awm e. Hmun himah inthiarfihlim nghal rawh u.",
    },
    "njz": {
        "language_name": "Nyishi",
        "script": "Latin",
        "state": "Arunachal Pradesh",
        "sms": "Hokum Hikan: {sec} ho nyem bopu runa nyi. {det}. Galang hoka melem nyodu.",
        "push_title": "[HOKUM] {sec} Nyem Bopu Alert",
        "push_body": "{sec} kela nyem bopu hikan bo. Ngunyik nyodu melem galang ho nyodu. Lambu kela: {det}.",
        "voice_script": "Nyanyi aji! {sec} ho nyem bopu hikan bo. Galang hoka melem nyodu.",
    },
    "nag": {
        "language_name": "Nagamese",
        "script": "Latin",
        "state": "Nagaland",
        "sms": "Hoshiar: {sec} te mati giribo nisina bisi dangor khatra ase. {det}. Jaldi safe jaga te jabi.",
        "push_title": "[HOSHIAR ALERT] {sec} Mati Giribo Ase",
        "push_body": "{sec} laga pahar rasta te mati giribo nisina dangor danger ase. Sob manu safe jaga te jabi. Dusra rasta: {det}.",
        "voice_script": "Sunibi sob manu! {sec} jaga te pahar mati giribo pare. Jaldi dusra rasta pora safe jaga jabi.",
    },
    "trp": {
        "language_name": "Kokborok",
        "script": "Latin",
        "state": "Tripura",
        "sms": "Sakrom Rwchapmung: {sec}o haphang bai mani khatra tongo. {det}. Safe thani tlangdi.",
        "push_title": "[SAKROM] {sec} Haphang Baimani Alert",
        "push_body": "{sec} haphang bai mani khatra tongo. Borokrok khorang thani tlangdi. Lama gubun: {det}.",
        "voice_script": "Naisingdi borokrok! {sec} haphang bai mani khatra tongo. Safe thani tlangdi.",
    },
    "pnar": {
        "language_name": "Pnar",
        "script": "Latin",
        "state": "Meghalaya (Jaintia Hills)",
        "sms": "I Pyntip: Ka ktieh ka ba tlep ha {sec}. {det}. Psiah cha ki thaw ba suk kloi.",
        "push_title": "[PYNTIP] Ka Ktieh Tlep ha {sec}",
        "push_body": "Ka ktieh kawa khroo ka ba tlep ha sarok {sec}. Lai cha ki thaw kiwa suk wa khlem tyrwa. Sarok da pyrkhat: {det}.",
        "voice_script": "Sngewbha khie! Ka ktieh kawa tlep ha {sec}. Psiah cha ki thaw ba suk kloi-kloi.",
    },
    "en": {
        "language_name": "English",
        "script": "Latin",
        "state": "National",
        "sms": "EMERGENCY: Severe landslide threat at {sec}. {det}. Move to safe ground immediately.",
        "push_title": "[EMERGENCY ALERT] Landslide Warning for {sec}",
        "push_body": "Critical hillslope instability detected at {sec}. Immediate evacuation advised. Alternate corridor: {det}.",
        "voice_script": "Emergency announcement. Severe landslide threat detected at {sec}. Evacuate immediately via designated detour routes.",
    },
    "hi": {
        "language_name": "Hindi",
        "script": "Devanagari",
        "state": "National",
        "sms": "आपातकालीन चेतावनी: {sec} पर भूस्खलन का भारी खतरा। {det}। तुरंत सुरक्षित स्थान पर जाएं।",
        "push_title": "[आपातकालीन चेतावनी] {sec} भूस्खलन चेतावनी",
        "push_body": "{sec} पहाड़ी क्षेत्र में गंभीर भूस्खलन की चेतावनी। तुरंत सुरक्षित स्थान पर जाएं। वैकल्पिक मार्ग: {det}।",
        "voice_script": "कृपया ध्यान दें। {sec} क्षेत्र में गंभीर भूस्खलन की चेतावनी जारी की गई है। तुरंत सुरक्षित स्थान पर जाएं।",
    },
}


class NERMultilingualSynthesizer:
    """
    Multilingual alert generator supporting 9 North-Eastern Region (NER)
    dialects plus English and Hindi.
    """

    def __init__(self) -> None:
        self.supported_codes = ALL_SUPPORTED_LANGUAGES
        self.ner_codes = NER_DIALECT_CODES

    @staticmethod
    def _truncate_sms(text: str, max_len: int = 158) -> str:
        """Enforce strict SMS character count limit (< 160 characters)."""
        if len(text) <= max_len:
            return text
        return text[:max_len - 3] + "..."

    def translate_alert(
        self,
        severity: str,
        sector_name: str,
        detour_info: str = "Use marked emergency bypass",
    ) -> Dict[str, Any]:
        """
        Synthesize localized alert payloads across all 9 NER languages + EN + HI.

        Parameters
        ----------
        severity : str
            Risk severity (e.g., "EXTREME", "SEVERE", "CRITICAL", "MODERATE")
        sector_name : str
            Target sector identifier (e.g., "NH-10 Km 48")
        detour_info : str
            Recommended evacuation or traffic diversion instructions

        Returns
        -------
        dict
            Contains:
            - Direct language code keys ('as', 'kha', etc.)
            - 'translations': dictionary of all language objects
            - 'languages': dictionary of all language objects
            - 'ner_languages': list of 9 NER language codes
            - 'metadata': overview information
        """
        sec = str(sector_name or "NH-10 Himalayan Corridor").strip()
        det = str(detour_info or "Follow local emergency detour signs").strip()
        sev = str(severity or "CRITICAL").upper()

        translations: Dict[str, Dict[str, Any]] = {}

        for code, meta in _TEMPLATES.items():
            raw_sms = meta["sms"].format(sec=sec, det=det)
            final_sms = self._truncate_sms(raw_sms)

            push_title = meta["push_title"].format(sec=sec)
            push_body = meta["push_body"].format(sec=sec, det=det)
            voice_script = meta["voice_script"].format(sec=sec)

            entry = {
                "code": code,
                "language_name": meta["language_name"],
                "script": meta["script"],
                "state": meta["state"],
                "sms": final_sms,
                "sms_length": len(final_sms),
                "push_title": push_title,
                "push_body": push_body,
                "voice_script": voice_script,
                "rich_push": {
                    "title": push_title,
                    "body": push_body,
                    "action": "EVACUATE",
                    "severity": sev,
                    "detour": det,
                },
            }
            translations[code] = entry

        # Assemble unified response with top-level convenience accessors
        response: Dict[str, Any] = {
            "status": "SUCCESS",
            "severity": sev,
            "sector_name": sec,
            "detour_info": det,
            "ner_languages": self.ner_codes,
            "all_languages": self.supported_codes,
            "translations": translations,
            "languages": translations,
            "provenance": "[SIMULATED] NE-BERT Multilingual Alert Synthesizer v1",
        }

        # Also expose language codes directly at top level for effortless lookup
        for code, data in translations.items():
            response[code] = data

        return response

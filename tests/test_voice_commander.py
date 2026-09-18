"""Unit and integration tests for OmniRoute AI Voice Commander & Multi-Dialect Acoustic Briefing Engine.

Validates Rule 7 (OmniRoute Fail-Safe Invariant) and Multilingual Acoustic Safety:
- ITU-T 960Hz / 800Hz dual-tone emergency preamble chime parameters
- Multi-dialect speech synthesis scripts (en-IN, hi-IN, ne-NP)
- Circuit-breaker graceful fallback from local OmniRoute LLM (localhost:20128) to deterministic synthesis
- Corroborated modality inclusion (FoS, InSAR, DWR, Crack Aperture, Detour)
- REST endpoints GET & POST /api/voice/briefing
"""

import os
os.environ["PARVAT_TESTING"] = "1"
import unittest
import json
from app import app
from services.ai_voice_commander import ai_voice_commander


class TestAIVoiceCommander(unittest.TestCase):
    """Test suite for OmniRoute AI Voice Commander briefing service."""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_voice_briefing_get_default(self):
        """Verify GET /api/voice/briefing returns standard tactical SitRep with chime meta."""
        res = self.client.get("/api/voice/briefing")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("sector_id"), "SK-NH10-KM48")
        self.assertEqual(data.get("language"), "en")
        self.assertIn("sitrep_tactical_text", data)
        self.assertIn("voice_script", data)
        self.assertIn("chime_audio_meta", data)
        self.assertIn("provenance", data)

        # Invariant: Provenance must be explicit
        self.assertIn(data["provenance"], ["[OMNIROUTE / LLM-ENRICHED]", "[LIVE / DETERMINISTIC]"])

        # Invariant: ITU-T 960Hz -> 800Hz Dual-Tone Preamble parameters
        chime = data["chime_audio_meta"]
        self.assertEqual(chime.get("primary_freq_hz"), 960.0)
        self.assertEqual(chime.get("secondary_freq_hz"), 800.0)
        self.assertEqual(chime.get("duration_ms"), 600)
        self.assertEqual(chime.get("waveform"), "sine")

    def test_voice_briefing_post_multidialects(self):
        """Verify POST /api/voice/briefing generates localized voice scripts in Nepali and Hindi."""
        # Nepali Request
        res_ne = self.client.post("/api/voice/briefing", json={
            "sector_id": "SK-NH10-KM48",
            "language": "ne",
            "crack_aperture_mm": 42.5
        })
        self.assertEqual(res_ne.status_code, 200)
        d_ne = res_ne.get_json()
        self.assertTrue(d_ne["success"])
        self.assertEqual(d_ne["language"], "ne")
        self.assertEqual(d_ne["speech_synthesis_code"], "ne-NP")
        # Ensure Nepali script contains Devanagari text
        self.assertTrue(any(ord(c) >= 0x0900 and ord(c) <= 0x097F for c in d_ne["voice_script"]))

        # Hindi Request
        res_hi = self.client.post("/api/voice/briefing", json={
            "sector_id": "SK-NH10-KM48",
            "language": "hi"
        })
        self.assertEqual(res_hi.status_code, 200)
        d_hi = res_hi.get_json()
        self.assertTrue(d_hi["success"])
        self.assertEqual(d_hi["language"], "hi")
        self.assertEqual(d_hi["speech_synthesis_code"], "hi-IN")
        self.assertTrue(any(ord(c) >= 0x0900 and ord(c) <= 0x097F for c in d_hi["voice_script"]))

    def test_voice_briefing_corroborates_modalities(self):
        """Verify the generated SitRep corroborates multimodal telemetry including tension cracks."""
        res = self.client.post("/api/voice/briefing", json={
            "sector_id": "SK-NH10-KM48",
            "language": "en",
            "fos": 0.48,
            "insar_velocity": -34.2,
            "crack_aperture_mm": 42.5
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        modalities = data.get("modalities_corroborated", {})
        self.assertEqual(modalities.get("fos"), 0.48)
        self.assertEqual(modalities.get("insar_velocity_mm_yr"), -34.2)
        self.assertEqual(modalities.get("crack_aperture_mm"), 42.5)
        self.assertTrue(modalities.get("crack_breach_active"))
        self.assertIn("NH-717A", data.get("tactical_action_enforced", ""))

    def test_service_resilience_when_omniroute_offline(self):
        """Verify AIVoiceCommanderService deterministically synthesizes briefing if OmniRoute is offline."""
        briefing = ai_voice_commander.generate_briefing(
            sector_id="ML-SONAPUR-KM142",
            language="en",
            force_deterministic=True
        )
        self.assertTrue(briefing["success"])
        self.assertEqual(briefing["provenance"], "[LIVE / DETERMINISTIC]")
        self.assertIn("SONAPUR", briefing["sitrep_tactical_text"].upper())
        self.assertIn("chime_audio_meta", briefing)


if __name__ == "__main__":
    unittest.main()

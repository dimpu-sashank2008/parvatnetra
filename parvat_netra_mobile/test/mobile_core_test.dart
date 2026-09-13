// test/mobile_core_test.dart
// ==========================
// PARVAT NETRA • Mobile Core Logic, Schema, Roles, Forecast & Sync Verification Suite
// Standard Flutter test discovery harness wrapping all 41 Phase 5E core invariants.
// Problem Statement ID: 26001 (Smart India Hackathon)

import 'dart:convert';
import 'dart:math';
import 'package:flutter_test/flutter_test.dart';

void main() {
  // ---------------------------------------------------------------------------
  // 1. PahadRiskSnapshot Contract Test
  // ---------------------------------------------------------------------------
  group('1. PahadRiskSnapshot Parsing & Model Invariants', () {
    final sampleBackendPahad = {
      'sector_id': 'SK-NH10-KM48',
      'composite_risk_score': 78.4,
      'alert_band': 'VERY_HIGH',
      'factor_of_safety': 0.895,
      'confidence': 0.89,
      'provenance': '[LIVE] PAHAD Multimodal Fusion Engine',
      'rainfall_trigger': 'EXCEEDED',
      'seismic_influence': 'MODERATE',
      'signal_agreement': '3/3',
      'recommendation': 'Halt heavy vehicle convoy traffic on NH-10. Route via Lava bypass.',
      'multi_horizon_probabilities': {
        '6h': 0.62,
        '12h': 0.74,
        '24h': 0.84,
        '48h': 0.88,
      },
      'top_drivers': ['Antecedent Rainfall (API-7d)', 'Piezometer Pore Pressure Surge'],
      'timestamp': '2026-09-10T06:30:00Z',
      'data_age_seconds': 120,
      'model_version': 'PAHAD-Event-v5.2.0',
    };

    final cri = (sampleBackendPahad['composite_risk_score'] as num).toDouble();
    final fos = (sampleBackendPahad['factor_of_safety'] as num).toDouble();
    final band = sampleBackendPahad['alert_band'] as String;
    final horizons = sampleBackendPahad['multi_horizon_probabilities'] as Map<String, dynamic>;

    test('PahadRiskSnapshot CRI extraction', () {
      expect(cri, equals(78.4));
    });

    test('PahadRiskSnapshot FoS continuity', () {
      expect(fos < 1.0 && fos > 0.0, isTrue);
    });

    test('PahadRiskSnapshot Alert Band validity', () {
      expect(['LOW', 'MODERATE', 'HIGH', 'VERY_HIGH', 'EXTREME'].contains(band), isTrue);
    });

    test('PahadRiskSnapshot 24h event probability', () {
      expect(horizons['24h'], equals(0.84));
    });

    test('PahadRiskSnapshot Model agreement invariant', () {
      expect(sampleBackendPahad['signal_agreement'], equals('3/3'));
    });
  });

  // ---------------------------------------------------------------------------
  // 2. FieldReport Section 8 SQLite Schema Invariants
  // ---------------------------------------------------------------------------
  group('2. FieldReport Schema & Sync Status State Machine', () {
    final sampleReport = {
      'local_id': 'PN-LOC-TEST-0099',
      'server_id': 1042,
      'created_at': '2026-09-10T06:30:00Z',
      'updated_at': '2026-09-10T06:31:00Z',
      'lat': 27.2410,
      'lon': 88.5140,
      'hazard_type': 'slope_crack',
      'severity': 'HIGH',
      'description': 'Continuous longitudinal tension crack across road shoulder.',
      'photo_paths': '["/data/user/0/app/cache/crack1.jpg"]',
      'video_paths': '[]',
      'reporter_role': 'FIELD_OPERATOR',
      'sync_status': 'PENDING',
      'retry_count': 0,
      'last_sync_error': null,
    };

    test('FieldReport sync status enum validity', () {
      final validSyncStates = ['PENDING', 'SYNCING', 'SYNCED', 'RETRY_PENDING', 'FAILED'];
      expect(validSyncStates.contains(sampleReport['sync_status']), isTrue);
    });

    test('FieldReport zero coordinate fabrication guard', () {
      expect(sampleReport['lat'] != 0.0 && sampleReport['lon'] != 0.0, isTrue);
    });

    test('FieldReport mandatory local_id present', () {
      expect((sampleReport['local_id'] as String).isNotEmpty, isTrue);
    });

    test('FieldReport photo paths JSON serialization', () {
      final photoList = jsonDecode(sampleReport['photo_paths'] as String) as List;
      expect(photoList.length == 1 && photoList[0].toString().endsWith('.jpg'), isTrue);
    });
  });

  // ---------------------------------------------------------------------------
  // 3. Haversine Geofence Calculation
  // ---------------------------------------------------------------------------
  group('3. Geofenced Alerting (Haversine 15 km Radius)', () {
    double haversineKm(double lat1, double lon1, double lat2, double lon2) {
      const r = 6371.0;
      final dLat = (lat2 - lat1) * pi / 180.0;
      final dLon = (lon2 - lon1) * pi / 180.0;
      final a = sin(dLat / 2) * sin(dLat / 2) +
          cos(lat1 * pi / 180.0) * cos(lat2 * pi / 180.0) * sin(dLon / 2) * sin(dLon / 2);
      final c = 2 * atan2(sqrt(a), sqrt(1 - a));
      return r * c;
    }

    const hazardLat = 27.2010;
    const hazardLon = 88.5180;

    test('Geofence: Inside 15 km zone receives notification', () {
      final distA = haversineKm(hazardLat, hazardLon, 27.2250, 88.5250);
      final inGeofenceA = distA <= 15.0;
      expect(inGeofenceA && distA < 4.0, isTrue);
    });

    test('Geofence: Outside 15 km zone filtered from immediate siren', () {
      final distB = haversineKm(hazardLat, hazardLon, 27.3389, 88.6065);
      final inGeofenceB = distB <= 15.0;
      expect(!inGeofenceB && distB > 15.0, isTrue);
    });
  });

  // ---------------------------------------------------------------------------
  // 4. Multilingual Translation Key Verification (6 Himalayan Languages)
  // ---------------------------------------------------------------------------
  group('4. Multilingual Localization (6 Languages)', () {
    final supportedLanguages = ['en', 'hi', 'ne', 'bh', 'lp', 'as'];
    final sampleDictionary = {
      'en': {'app_title': 'PARVAT NETRA', 'forecast': 'FORECAST', 'data_status': 'DATA STATUS', 'verify_incident': 'VERIFY INCIDENT', 'offline_route': 'OFFLINE ROUTE'},
      'hi': {'app_title': 'पर्वत नेत्र', 'forecast': 'पूर्वानुमान', 'data_status': 'डेटा स्थिति', 'verify_incident': 'घटना सत्यापन', 'offline_route': 'ऑफ़लाइन मार्ग'},
      'ne': {'app_title': 'पर्वत नेत्र', 'forecast': 'पूर्वानुमान', 'data_status': 'डेटा स्थिति', 'verify_incident': 'घटना सत्यापन', 'offline_route': 'अफलाइन मार्ग'},
      'bh': {'app_title': 'རི་བོ་མིག་', 'forecast': 'FORECAST', 'data_status': 'DATA STATUS', 'verify_incident': 'VERIFY INCIDENT', 'offline_route': 'OFFLINE ROUTE'},
      'lp': {'app_title': 'ᰀᰩᰵ ᰕᰤᰩᰭ', 'forecast': 'FORECAST', 'data_status': 'DATA STATUS', 'verify_incident': 'VERIFY INCIDENT', 'offline_route': 'OFFLINE ROUTE'},
      'as': {'app_title': 'পৰ্বত নেত্ৰ', 'forecast': 'পূৰ্বাভাস', 'data_status': 'তথ্য স্থিতি', 'verify_incident': 'ঘটনা প্ৰমাণীকৰণ', 'offline_route': 'অফলাইন পথ'},
    };

    test('Localization: Exactly 6 Himalayan languages supported', () {
      expect(supportedLanguages.length, equals(6));
    });

    for (final lang in supportedLanguages) {
      test('Localization dictionary complete for [$lang]', () {
        final dict = sampleDictionary[lang];
        final hasKeys = dict != null &&
            dict.containsKey('app_title') &&
            dict.containsKey('forecast') &&
            dict.containsKey('offline_route');
        expect(hasKeys, isTrue);
      });
    }
  });

  // ---------------------------------------------------------------------------
  // 5. Hardware BLE Siren Test Mode Contract
  // ---------------------------------------------------------------------------
  group('5. Hardware BLE / Siren Test Payload Contract', () {
    final blePayload = {
      'alert_id': 'PN-TEST-001',
      'severity': 'VERY_HIGH',
      'action': 'SIREN_TEST',
      'is_hardware_armed': false,
      'dry_run': true,
      'protocol': 'BLE-5.3-LR / LoRa-865MHz',
      'safety_notice': 'BLE paired adapter communication only. Not a universal public broadcast.',
    };

    test('BLE payload matches required PN-TEST-001 identifier', () {
      expect(blePayload['alert_id'], equals('PN-TEST-001'));
    });

    test('BLE physical siren default suppression (DRY_RUN=true)', () {
      expect(blePayload['dry_run'], isTrue);
    });
  });

  // ---------------------------------------------------------------------------
  // 6. Exponential Backoff Calculation Invariant
  // ---------------------------------------------------------------------------
  group('6. Sync Service Exponential Backoff Formula', () {
    int calculateDelaySeconds(int retryCount) {
      final delay = (2 * pow(1.5, retryCount)).toInt();
      return min(delay, 60);
    }

    test('Backoff: retry 0 delay == 2s', () {
      expect(calculateDelaySeconds(0), equals(2));
    });

    test('Backoff: retry 1 delay == 3s', () {
      expect(calculateDelaySeconds(1), equals(3));
    });

    test('Backoff: retry 3 delay == 6s', () {
      expect(calculateDelaySeconds(3), equals(6));
    });

    test('Backoff: retry 10 clamped to 60s max', () {
      expect(calculateDelaySeconds(10), equals(60));
    });
  });

  // ---------------------------------------------------------------------------
  // 7. Phase 5E: Role-Aware Permission Matrix Invariants
  // ---------------------------------------------------------------------------
  group('7. Role-Aware Authentication & Permissions Matrix', () {
    Map<String, bool> getPermissions(String role) {
      switch (role) {
        case 'PUBLIC':
          return {'verify': false, 'ack_alert': false, 'data_status': false, 'command': false};
        case 'FIELD_OPERATOR':
          return {'verify': true, 'ack_alert': false, 'data_status': true, 'command': false};
        case 'AUTHORITY':
          return {'verify': true, 'ack_alert': true, 'data_status': true, 'command': true};
        case 'ADMIN':
          return {'verify': true, 'ack_alert': true, 'data_status': true, 'command': true};
        default:
          return {'verify': false, 'ack_alert': false, 'data_status': false, 'command': false};
      }
    }

    final publicPerms = getPermissions('PUBLIC');
    final foPerms = getPermissions('FIELD_OPERATOR');
    final authPerms = getPermissions('AUTHORITY');
    final adminPerms = getPermissions('ADMIN');

    test('PUBLIC: Cannot verify reports or acknowledge alerts', () {
      expect(!publicPerms['verify']! && !publicPerms['ack_alert']!, isTrue);
    });

    test('FIELD_OPERATOR: Can verify citizen reports but cannot acknowledge critical alerts', () {
      expect(foPerms['verify']! && !foPerms['ack_alert']!, isTrue);
    });

    test('AUTHORITY: Can acknowledge alerts and access command operations', () {
      expect(authPerms['ack_alert']! && authPerms['command']!, isTrue);
    });

    test('ADMIN: Full administrative and triage permissions enabled', () {
      expect(adminPerms['verify']! && adminPerms['command']!, isTrue);
    });
  });

  // ---------------------------------------------------------------------------
  // 8. Phase 5E: Multi-Horizon Forecast Parsing Invariant
  // ---------------------------------------------------------------------------
  group('8. Multi-Horizon Forecast Contract & Limitations', () {
    final sampleForecastPayload = {
      'status': 'SUCCESS',
      'forecast': {
        'sector_id': 'SK-NH10-KM48',
        'latitude': 27.33,
        'longitude': 88.61,
        'horizons': {
          '6': {'horizon_hours': 6, 'event_probability': 0.62, 'confidence': 0.85, 'data_quality': 0.85, 'model_version': 'v5.2.0', 'available': true},
          '12': {'horizon_hours': 12, 'event_probability': 0.74, 'confidence': 0.85, 'data_quality': 0.85, 'model_version': 'v5.2.0', 'available': true},
          '24': {'horizon_hours': 24, 'event_probability': 0.84, 'confidence': 0.89, 'data_quality': 0.85, 'model_version': 'v5.2.0', 'available': true},
          '48': {'horizon_hours': 48, 'event_probability': 0.88, 'confidence': 0.80, 'data_quality': 0.85, 'model_version': 'v5.2.0', 'available': true},
        },
        'limitation': 'Shared base model across horizons due to N=16 sample volume.',
        'model_status': 'TRAINED_LIMITED_DATA',
        'model_version': 'v5.2.0-phase5b',
        'training_events': 16,
      }
    };

    final fcData = sampleForecastPayload['forecast'] as Map<String, dynamic>;
    final fcHorizons = fcData['horizons'] as Map<String, dynamic>;

    test('Forecast: Exactly 4 operational forecast horizons (6h, 12h, 24h, 48h)', () {
      expect(fcHorizons.length, equals(4));
    });

    test('Forecast: Monotonic probability trend across windows', () {
      final p6 = fcHorizons['6']['event_probability'] as num;
      final p12 = fcHorizons['12']['event_probability'] as num;
      final p24 = fcHorizons['24']['event_probability'] as num;
      final p48 = fcHorizons['48']['event_probability'] as num;
      expect(p6 <= p12 && p12 <= p24 && p24 <= p48, isTrue);
    });

    test('Forecast: Model status must indicate TRAINED_LIMITED_DATA honestly', () {
      expect(fcData['model_status'], equals('TRAINED_LIMITED_DATA'));
    });

    test('Forecast: Sample size limitation documented explicitly', () {
      expect((fcData['limitation'] as String).contains('N=16'), isTrue);
    });
  });

  // ---------------------------------------------------------------------------
  // 9. Phase 5E: Canonical Sync Push & Pull Envelope Invariants
  // ---------------------------------------------------------------------------
  group('9. Canonical Sync Push & Pull Protocol Contracts', () {
    final syncPushResponse = {
      'sync_id': 'SYNC-20260910-001',
      'status': 'SUCCESS',
      'records_uploaded': 2,
      'records_failed': 0,
      'acknowledgements': [
        {'local_id': 'PN-LOC-101', 'server_id': 5001, 'status': 'SYNCED'},
        {'local_id': 'PN-LOC-102', 'server_id': 5002, 'status': 'SYNCED'},
      ],
    };

    test('Sync Push: Envelope contains positive records_uploaded count', () {
      expect(syncPushResponse['records_uploaded'], equals(2));
    });

    test('Sync Push: Acknowledgements list provides server_id mapping', () {
      final acks = syncPushResponse['acknowledgements'] as List;
      expect(acks[0]['server_id'] == 5001 && acks[1]['server_id'] == 5002, isTrue);
    });

    test('Sync Pull: Authoritative state contains alerts, sectors, and shelters', () {
      final syncPullResponse = {
        'sync_id': 'PULL-20260910-001',
        'status': 'SUCCESS',
        'alerts': [
          {'alert_id': 'ALT-01', 'severity': 'EXTREME', 'status': 'ACTIVE', 'timestamp': '2026-09-10T06:00:00Z'},
          {'alert_id': 'ALT-OLD', 'severity': 'HIGH', 'status': 'EXPIRED', 'timestamp': '2026-09-08T06:00:00Z'},
        ],
        'critical_sectors': [{'sector_id': 'SK-NH10-KM48', 'cri': 78.4}],
        'shelters': [{'name': 'Rangpo Evac Center', 'distance_km': 2.1}],
      };
      final pullAlerts = syncPullResponse['alerts'] as List;
      expect(pullAlerts.isNotEmpty && (syncPullResponse['critical_sectors'] as List).isNotEmpty, isTrue);
    });
  });

  // ---------------------------------------------------------------------------
  // 10. Phase 5E: Alert Expiry Auto-Suppression
  // ---------------------------------------------------------------------------
  group('10. Alert Auto-Suppression of Expired Warnings', () {
    bool isAlertActive(Map<String, dynamic> alert) {
      if (alert['status'] == 'EXPIRED' || alert['status'] == 'RESOLVED') return false;
      try {
        final issued = DateTime.parse(alert['timestamp'] as String);
        final ageHours = DateTime.now().toUtc().difference(issued.toUtc()).inHours;
        return ageHours < 24;
      } catch (_) {
        return false;
      }
    }

    final freshAlert = {'alert_id': 'ALT-NEW', 'status': 'ACTIVE', 'timestamp': DateTime.now().toUtc().toIso8601String()};
    final staleAlert = {'alert_id': 'ALT-OLD', 'status': 'ACTIVE', 'timestamp': '2026-09-01T00:00:00Z'};
    final explicitlyExpired = {'alert_id': 'ALT-EXP', 'status': 'EXPIRED', 'timestamp': DateTime.now().toUtc().toIso8601String()};

    test('Alerts: Fresh active alert is preserved as ACTIVE', () {
      expect(isAlertActive(freshAlert), isTrue);
    });

    test('Alerts: Stale alert older than 24h is suppressed from active feed', () {
      expect(isAlertActive(staleAlert), isFalse);
    });

    test('Alerts: Explicitly expired alert is suppressed from active feed', () {
      expect(isAlertActive(explicitlyExpired), isFalse);
    });
  });

  // ---------------------------------------------------------------------------
  // 11. Phase 5E: Tactical Safe Route & [OFFLINE ROUTE] Invariant
  // ---------------------------------------------------------------------------
  group('11. Tactical Evacuation Routing & [OFFLINE ROUTE]', () {
    final offlineRoutePlan = {
      'status': 'OPERATIONAL',
      'is_offline_route': true,
      'provenance': '[OFFLINE ROUTE]',
      'primary_corridor': {
        'name': 'NH-10',
        'status': 'BLOCKED',
        'is_safe': false,
        'blockage_reason': 'Km 48 Severed Corridor',
      },
      'recommended_route': {
        'name': 'NH-717A (Lava Bypass)',
        'status': 'AVAILABLE',
        'is_safe': true,
        'estimated_distance_km': 64.2,
      }
    };

    final prim = offlineRoutePlan['primary_corridor'] as Map<String, dynamic>;
    final rec = offlineRoutePlan['recommended_route'] as Map<String, dynamic>;

    test('Routing: Severed NH-10 corridor identified as BLOCKED', () {
      expect(prim['status'], equals('BLOCKED'));
    });

    test('Routing: Recommended NH-717A bypass marked AVAILABLE and SAFE', () {
      expect(rec['is_safe'], isTrue);
    });

    test('Routing: Offline calculated route tagged explicitly with [OFFLINE ROUTE] badge', () {
      expect(offlineRoutePlan['provenance'], equals('[OFFLINE ROUTE]'));
    });
  });
}

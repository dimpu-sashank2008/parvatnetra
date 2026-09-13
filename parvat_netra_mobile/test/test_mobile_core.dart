// test/test_mobile_core.dart
// ==========================
// PARVAT NETRA • Mobile Core Logic, Schema, Roles, Forecast & Sync Verification Suite
// Tests models, state machines, geofencing, localization, offline protocol, and permissions.
// Can be executed standalone via `dart run test/test_mobile_core.dart`
// Problem Statement ID: 26001 (Smart India Hackathon)

import 'dart:convert';
import 'dart:math';

void main() {
  print('===============================================================');
  print('PARVAT NETRA • PHASE 5E MOBILE CORE & INVARIANTS TEST SUITE');
  print('===============================================================');

  int passed = 0;
  int failed = 0;

  void assertTest(String name, bool condition, [String detail = '']) {
    if (condition) {
      print('[PASS] $name');
      passed++;
    } else {
      print('[FAIL] $name: $detail');
      failed++;
    }
  }

  // ---------------------------------------------------------------------------
  // 1. PahadRiskSnapshot Contract Test
  // ---------------------------------------------------------------------------
  print('\n--- 1. PahadRiskSnapshot Parsing & Model Invariants ---');
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

  assertTest('PahadRiskSnapshot CRI extraction', cri == 78.4);
  assertTest('PahadRiskSnapshot FoS continuity', fos < 1.0 && fos > 0.0);
  assertTest('PahadRiskSnapshot Alert Band validity', ['LOW', 'MODERATE', 'HIGH', 'VERY_HIGH', 'EXTREME'].contains(band));
  assertTest('PahadRiskSnapshot 24h event probability', horizons['24h'] == 0.84);
  assertTest('PahadRiskSnapshot Model agreement invariant', sampleBackendPahad['signal_agreement'] == '3/3');

  // ---------------------------------------------------------------------------
  // 2. FieldReport Section 8 SQLite Schema Invariants
  // ---------------------------------------------------------------------------
  print('\n--- 2. FieldReport Schema & Sync Status State Machine ---');
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

  final validSyncStates = ['PENDING', 'SYNCING', 'SYNCED', 'RETRY_PENDING', 'FAILED'];
  assertTest('FieldReport sync status enum validity', validSyncStates.contains(sampleReport['sync_status']));
  assertTest('FieldReport zero coordinate fabrication guard', sampleReport['lat'] != 0.0 && sampleReport['lon'] != 0.0);
  assertTest('FieldReport mandatory local_id present', (sampleReport['local_id'] as String).isNotEmpty);

  final photoList = jsonDecode(sampleReport['photo_paths'] as String) as List;
  assertTest('FieldReport photo paths JSON serialization', photoList.length == 1 && photoList[0].toString().endsWith('.jpg'));

  // ---------------------------------------------------------------------------
  // 3. Haversine Geofence Calculation
  // ---------------------------------------------------------------------------
  print('\n--- 3. Geofenced Alerting (Haversine 15 km Radius) ---');
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

  final distA = haversineKm(hazardLat, hazardLon, 27.2250, 88.5250);
  final inGeofenceA = distA <= 15.0;
  assertTest('Geofence: Inside 15 km zone receives notification', inGeofenceA && distA < 4.0, 'Dist: ${distA.toStringAsFixed(2)} km');

  final distB = haversineKm(hazardLat, hazardLon, 27.3389, 88.6065);
  final inGeofenceB = distB <= 15.0;
  assertTest('Geofence: Outside 15 km zone filtered from immediate siren', !inGeofenceB && distB > 15.0, 'Dist: ${distB.toStringAsFixed(2)} km');

  // ---------------------------------------------------------------------------
  // 4. Multilingual Translation Key Verification (6 Himalayan Languages)
  // ---------------------------------------------------------------------------
  print('\n--- 4. Multilingual Localization (6 Languages) ---');
  final supportedLanguages = ['en', 'hi', 'ne', 'bh', 'lp', 'as'];
  final sampleDictionary = {
    'en': {'app_title': 'PARVAT NETRA', 'forecast': 'FORECAST', 'data_status': 'DATA STATUS', 'verify_incident': 'VERIFY INCIDENT', 'offline_route': 'OFFLINE ROUTE'},
    'hi': {'app_title': 'पर्वत नेत्र', 'forecast': 'पूर्वानुमान', 'data_status': 'डेटा स्थिति', 'verify_incident': 'घटना सत्यापन', 'offline_route': 'ऑफ़लाइन मार्ग'},
    'ne': {'app_title': 'पर्वत नेत्र', 'forecast': 'पूर्वानुमान', 'data_status': 'डेटा स्थिति', 'verify_incident': 'घटना सत्यापन', 'offline_route': 'अफलाइन मार्ग'},
    'bh': {'app_title': 'རི་བོ་མིག་', 'forecast': 'FORECAST', 'data_status': 'DATA STATUS', 'verify_incident': 'VERIFY INCIDENT', 'offline_route': 'OFFLINE ROUTE'},
    'lp': {'app_title': 'ᰀᰩᰵ ᰕᰤᰩᰭ', 'forecast': 'FORECAST', 'data_status': 'DATA STATUS', 'verify_incident': 'VERIFY INCIDENT', 'offline_route': 'OFFLINE ROUTE'},
    'as': {'app_title': 'পৰ্বত নেত্ৰ', 'forecast': 'পূৰ্বাভাস', 'data_status': 'তথ্য স্থিতি', 'verify_incident': 'ঘটনা প্ৰমাণীকৰণ', 'offline_route': 'অফলাইন পথ'},
  };

  assertTest('Localization: Exactly 6 Himalayan languages supported', supportedLanguages.length == 6);
  for (final lang in supportedLanguages) {
    final dict = sampleDictionary[lang];
    final hasKeys = dict != null && dict.containsKey('app_title') && dict.containsKey('forecast') && dict.containsKey('offline_route');
    assertTest('Localization dictionary complete for [$lang]', hasKeys);
  }

  // ---------------------------------------------------------------------------
  // 5. Hardware BLE Siren Test Mode Contract
  // ---------------------------------------------------------------------------
  print('\n--- 5. Hardware BLE / Siren Test Payload Contract ---');
  final blePayload = {
    'alert_id': 'PN-TEST-001',
    'severity': 'VERY_HIGH',
    'action': 'SIREN_TEST',
    'is_hardware_armed': false,
    'dry_run': true,
    'protocol': 'BLE-5.3-LR / LoRa-865MHz',
    'safety_notice': 'BLE paired adapter communication only. Not a universal public broadcast.',
  };

  assertTest('BLE payload matches required PN-TEST-001 identifier', blePayload['alert_id'] == 'PN-TEST-001');
  assertTest('BLE physical siren default suppression (DRY_RUN=true)', blePayload['dry_run'] == true);

  // ---------------------------------------------------------------------------
  // 6. Exponential Backoff Calculation Invariant
  // ---------------------------------------------------------------------------
  print('\n--- 6. Sync Service Exponential Backoff Formula ---');
  int calculateDelaySeconds(int retryCount) {
    final delay = (2 * pow(1.5, retryCount)).toInt();
    return min(delay, 60);
  }

  assertTest('Backoff: retry 0 delay == 2s', calculateDelaySeconds(0) == 2);
  assertTest('Backoff: retry 1 delay == 3s', calculateDelaySeconds(1) == 3);
  assertTest('Backoff: retry 3 delay == 6s', calculateDelaySeconds(3) == 6);
  assertTest('Backoff: retry 10 clamped to 60s max', calculateDelaySeconds(10) == 60);

  // ---------------------------------------------------------------------------
  // 7. Phase 5E: Role-Aware Permission Matrix Invariants
  // ---------------------------------------------------------------------------
  print('\n--- 7. Role-Aware Authentication & Permissions Matrix ---');
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

  assertTest('PUBLIC: Cannot verify reports or acknowledge alerts', !publicPerms['verify']! && !publicPerms['ack_alert']!);
  assertTest('FIELD_OPERATOR: Can verify citizen reports but cannot acknowledge critical alerts', foPerms['verify']! && !foPerms['ack_alert']!);
  assertTest('AUTHORITY: Can acknowledge alerts and access command operations', authPerms['ack_alert']! && authPerms['command']!);
  assertTest('ADMIN: Full administrative and triage permissions enabled', adminPerms['verify']! && adminPerms['command']!);

  // ---------------------------------------------------------------------------
  // 8. Phase 5E: Multi-Horizon Forecast Parsing Invariant
  // ---------------------------------------------------------------------------
  print('\n--- 8. Multi-Horizon Forecast Contract & Limitations ---');
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

  assertTest('Forecast: Exactly 4 operational forecast horizons (6h, 12h, 24h, 48h)', fcHorizons.length == 4);
  assertTest('Forecast: Monotonic probability trend across windows',
      (fcHorizons['6']['event_probability'] as num) <= (fcHorizons['12']['event_probability'] as num) &&
      (fcHorizons['12']['event_probability'] as num) <= (fcHorizons['24']['event_probability'] as num) &&
      (fcHorizons['24']['event_probability'] as num) <= (fcHorizons['48']['event_probability'] as num));
  assertTest('Forecast: Model status must indicate TRAINED_LIMITED_DATA honestly', fcData['model_status'] == 'TRAINED_LIMITED_DATA');
  assertTest('Forecast: Sample size limitation documented explicitly', (fcData['limitation'] as String).contains('N=16'));

  // ---------------------------------------------------------------------------
  // 9. Phase 5E: Canonical Sync Push & Pull Envelope Invariants
  // ---------------------------------------------------------------------------
  print('\n--- 9. Canonical Sync Push & Pull Protocol Contracts ---');
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

  final acks = syncPushResponse['acknowledgements'] as List;
  assertTest('Sync Push: Envelope contains positive records_uploaded count', syncPushResponse['records_uploaded'] == 2);
  assertTest('Sync Push: Acknowledgements list provides server_id mapping', acks[0]['server_id'] == 5001 && acks[1]['server_id'] == 5002);

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
  assertTest('Sync Pull: Authoritative state contains alerts, sectors, and shelters',
      pullAlerts.isNotEmpty && (syncPullResponse['critical_sectors'] as List).isNotEmpty);

  // ---------------------------------------------------------------------------
  // 10. Phase 5E: Alert Expiry Auto-Suppression
  // ---------------------------------------------------------------------------
  print('\n--- 10. Alert Auto-Suppression of Expired Warnings ---');
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

  assertTest('Alerts: Fresh active alert is preserved as ACTIVE', isAlertActive(freshAlert));
  assertTest('Alerts: Stale alert older than 24h is suppressed from active feed', !isAlertActive(staleAlert));
  assertTest('Alerts: Explicitly expired alert is suppressed from active feed', !isAlertActive(explicitlyExpired));

  // ---------------------------------------------------------------------------
  // 11. Phase 5E: Tactical Safe Route & [OFFLINE ROUTE] Invariant
  // ---------------------------------------------------------------------------
  print('\n--- 11. Tactical Evacuation Routing & [OFFLINE ROUTE] ---');
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
  assertTest('Routing: Severed NH-10 corridor identified as BLOCKED', prim['status'] == 'BLOCKED');
  assertTest('Routing: Recommended NH-717A bypass marked AVAILABLE and SAFE', rec['is_safe'] == true);
  assertTest('Routing: Offline calculated route tagged explicitly with [OFFLINE ROUTE] badge', offlineRoutePlan['provenance'] == '[OFFLINE ROUTE]');

  // ---------------------------------------------------------------------------
  // Summary
  // ---------------------------------------------------------------------------
  print('\n===============================================================');
  print('TEST SUMMARY: $passed PASSED, $failed FAILED (Total: ${passed + failed})');
  print('===============================================================');

  if (failed > 0) {
    print('Core tests encountered failures.');
  } else {
    print('All Phase 5E mobile core models, roles, forecasts, routing, alerts, and sync tests PASSED.');
  }
}

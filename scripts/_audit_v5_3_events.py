# -*- coding: utf-8 -*-
import json
import csv

print("=== BASELINE EVENTS (data/raw/historical_landslides_ner.csv) ===")
with open("data/raw/historical_landslides_ner.csv", "r", encoding="utf-8") as f:
    r = csv.DictReader(f)
    for row in r:
        print(f"{row['event_id']}: {row['disaster_id']} | {row['timestamp']} | ({row['latitude']}, {row['longitude']}) | {row['state']}, {row['district']} | {row['source']}")

print("\n=== EXPANSION EVENTS (data/raw/historical_landslides_expansion_v5_2.json) ===")
with open("data/raw/historical_landslides_expansion_v5_2.json", "r", encoding="utf-8") as f:
    exp = json.load(f)
    for item in exp:
        print(f"{item['event_id']}: {item['source_reference']} | {item['timestamp']} | ({item['latitude']}, {item['longitude']}) | {item['state']}, {item['district']} | {item['source']} | Tier: {item.get('verification_status')}")

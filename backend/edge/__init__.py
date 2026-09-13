# -*- coding: utf-8 -*-
"""
PARVAT NETRA / PAHAD AI - Edge Network Module
Phase 3.4 Local Edge Network + LoRa Mesh + BLE + Siren + Sensor Gateway
"""

from .packet import (
    EdgePacket,
    encode_packet,
    decode_packet,
    PROTOCOL_VERSION,
    PACKET_BINARY_LENGTH,
    PACKET_SIZE_BYTES,
    PACKET_STRUCT_FORMAT,
    PACKET_MAGIC,
    crc16_ccitt,
    node_id_to_hash16,
)
from .edge_store import EdgeStore
from .risk_evaluator import EdgeRiskEvaluator
from .siren_controller import SirenController
from .ble_bridge import BLEAlertBridge
from .mesh import LoRaMesh
from .sensor_node import SensorNode
from .sync import EdgeSync
from .adapters import (
    MockSensorAdapter,
    MockLoRaAdapter,
    MockBLEAdapter,
    MockSirenAdapter,
    MQTTAdapter,
)
from .gateway import EdgeGateway

__all__ = [
    "EdgePacket",
    "encode_packet",
    "decode_packet",
    "PROTOCOL_VERSION",
    "PACKET_BINARY_LENGTH",
    "PACKET_SIZE_BYTES",
    "PACKET_STRUCT_FORMAT",
    "PACKET_MAGIC",
    "crc16_ccitt",
    "node_id_to_hash16",
    "EdgeStore",
    "EdgeRiskEvaluator",
    "SirenController",
    "BLEAlertBridge",
    "LoRaMesh",
    "SensorNode",
    "EdgeSync",
    "MockSensorAdapter",
    "MockLoRaAdapter",
    "MockBLEAdapter",
    "MockSirenAdapter",
    "MQTTAdapter",
    "EdgeGateway",
]

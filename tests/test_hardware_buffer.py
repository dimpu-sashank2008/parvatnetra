# -*- coding: utf-8 -*-
"""
tests/test_hardware_buffer.py
=============================
Phase 6C Test Suite: Node-Side Local FIFO Buffer & Offline Ingestion
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from firmware.interfaces import LocalCircularBuffer
from firmware.esp32_node import ESP32SensorNode


class TestLocalCircularBuffer:

    def test_buffer_fifo_order(self):
        buf = LocalCircularBuffer(max_capacity=10)
        assert buf.is_empty() is True
        assert buf.count() == 0

        # Push 3 items
        buf.push({"seq": 1, "val": 10.0})
        buf.push({"seq": 2, "val": 20.0})
        buf.push({"seq": 3, "val": 30.0})

        assert buf.count() == 3
        assert buf.is_empty() is False

        # Peek oldest
        peeked = buf.peek()
        assert peeked["seq"] == 1

        # Pop oldest
        popped1 = buf.pop()
        assert popped1["seq"] == 1
        popped2 = buf.pop()
        assert popped2["seq"] == 2
        popped3 = buf.pop()
        assert popped3["seq"] == 3

        assert buf.is_empty() is True
        assert buf.pop() is None

    def test_buffer_capacity_circular_overwrite(self):
        buf = LocalCircularBuffer(max_capacity=3)
        buf.push({"seq": 1})
        buf.push({"seq": 2})
        buf.push({"seq": 3})
        assert buf.count() == 3

        # Pushing 4th item when capacity is 3 drops oldest (seq 1)
        buf.push({"seq": 4})
        assert buf.count() == 3

        popped = buf.pop()
        assert popped["seq"] == 2  # Seq 1 was evicted


class TestESP32NodeBufferingAndReplay:

    def test_node_offline_buffering_and_reconnection_replay(self):
        node = ESP32SensorNode(device_id="PZ-BUFF-TEST-01", sensor_type="piezometer")
        node.initialize()

        transmitted_packets = []

        def mock_sink(frame_bytes):
            transmitted_packets.append(frame_bytes)
            return True

        node.set_transmit_sink(mock_sink)

        # Step 1: Online - normal transmission
        res1 = node.step()
        assert res1["transmitted"] is True
        assert res1["buffered"] is False
        assert len(transmitted_packets) == 1
        assert node.buffer.count() == 0

        # Step 2: Radio link lost
        node.set_radio_connectivity(False)

        res2 = node.step()
        assert res2["transmitted"] is False
        assert res2["buffered"] is True
        assert node.buffer.count() == 1

        res3 = node.step()
        assert res3["transmitted"] is False
        assert res3["buffered"] is True
        assert node.buffer.count() == 2

        # Step 3: Radio link restored
        node.set_radio_connectivity(True)

        # Next step should replay backlog + transmit current
        res4 = node.step()
        assert res4["replayed_from_buffer"] == 2
        assert res4["transmitted"] is True
        assert node.buffer.count() == 0
        assert len(transmitted_packets) == 4  # res1 + 2 replayed + res4

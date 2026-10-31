import queue
import unittest
import unittest.mock

from pymilight.milight_control import MiLightController
from pymilight.packet_formatter import PyRgbCctPacketFormatter


class MiLightControllerTestCase(unittest.TestCase):
    def build_mocked_controller(self):
        formatter = PyRgbCctPacketFormatter()
        controller = MiLightController(None, None, None, True)
        controller.radios = {
            "rgb_cct": unittest.mock.MagicMock()
        }
        controller.radios["rgb_cct"].formatter = formatter
        return controller

    def run_packet_compare(self, request, expected):
        controller = self.build_mocked_controller()
        controller.set_bulb("rgb_cct", 0x2, 1)
        packets = list(controller.request_to_packets(request))
        self.assertEqual(len(expected), len(packets))
        for packet, expected_packet in zip(packets, expected):
            self.assertEqual(expected_packet, packet.hex())

    @unittest.mock.patch("pymilight.milight_control.RF24")
    def test_brightness_sent_after_mode(self, rf24):
        controller = self.build_mocked_controller()
        controller.set_bulb("rgb_cct", 0x2, 1)
        request = {"state": "ON", "brightness": 255, "color_temp": 370}
        expected = list(controller.request_to_packets({"color_temp": 370}))[0]

        packets = list(controller.request_to_packets(request))

        self.assertEqual(3, len(packets))
        # Sequence number and checksum differ, command and argument bytes must match.
        self.assertEqual(expected[4:6], packets[1][4:6])

    @unittest.mock.patch("pymilight.milight_control.RF24")
    def test_remote_packet_updates_state(self, rf24):
        controller = self.build_mocked_controller()
        controller.outbound_queue = queue.Queue()
        controller.set_bulb("rgb_cct", 0xABCD, 3)
        packet = bytearray(controller.radios["rgb_cct"].formatter.update_status(True))
        radio = controller.radios["rgb_cct"]
        radio.available.side_effect = [True, True, False]
        radio.read.return_value = packet

        controller.process_radio()

        self.assertEqual(
            ("rgb_cct", 0xABCD, 3, {"state": "ON"}),
            controller.outbound_queue.get_nowait(),
        )

    @unittest.mock.patch("pymilight.milight_control.RF24")
    def test_packet_on(self, rf24):
        self.run_packet_compare(
            {"state": "on"},
            ["00dbe12166d1ba66cc"],
        )
    
    @unittest.mock.patch("pymilight.milight_control.RF24")
    def test_packet_white(self, rf24):
        self.run_packet_compare(
            {
                "state": "ON",
                "color_temp": 370,
                "bulb_mode": "white",
                "color":{"r": 255, "g": 255, "b": 255}
            },
            [
                "00dbe12166d1ba66cc",
                "00dbe1216494bb667e",
                "00dbe1216494b8667b",
            ]
        )
        
    @unittest.mock.patch("pymilight.milight_control.RF24")
    def test_packet_mode(self, rf24):
        self.run_packet_compare(
            {
                "state": "ON",
                "mode": 3,
                "bulb_mode": "scene",
                "color": {"r": 255, "g": 255, "b": 255}
            },
            [
                "00dbe12166d1ba66cc",
                "00dbe1216494bb667e",
                "00dbe12162cfb866b4",
            ]
        )
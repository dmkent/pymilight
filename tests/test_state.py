import json
import unittest

from pymilight.state import State, BULB_MODE_COLOR, BULB_MODE_SCENE, BULB_MODE_NIGHT, BULB_MODE_WHITE


class MiLightStateTestCase(unittest.TestCase):
    def test_dump_load(self):
        state = State()
        state.state = True
        dumped = state.dump()
        self.assertEqual({
            "_saturation": None,
            "_mode": None,
            "_brightness_mode": None,
            "_brightness_color": None,
            "_night_mode": None,
            "_bulb_mode": None,
            "_state": True,
            "_dirty": True,
            "_mqtt_dirty": True,
            "_hue": None,
            "_brightness": None,
            "_white_val": None,
        }, json.loads(dumped))

        state2 = State()
        state2.load(dumped)
        self.assertTrue(state2.state)

    def test_apply_state1(self):
        state = State()
        state.state = True
        state.bulb_mode = BULB_MODE_COLOR
        state.brightness = 67
        state.hue = 200
        state.saturation = 100

        result = {}
        state.apply_state(result)

        self.assertEqual({
            "brightness": 171,
            "level": 67,
            "state": "ON",
            "color": {"b": 255, "g": 169, "r": 0},
            "hue": 200,
            "saturation": 100,
            "bulb_mode": "color",
            "color_mode": "rgb"
        }, result)

    def test_apply_state2(self):
        state = State()
        state.state = True
        state.mode = 2
        state.bulb_mode = BULB_MODE_SCENE

        result = {}
        state.apply_state(result)

        self.assertEqual({
            "state": "ON",
            "color": {"b": 255, "g": 255, "r": 255},
            "bulb_mode": "scene",
            "effect": '2',
            "mode": 2
        }, result)

    def test_apply_night(self):
        state = State()
        state.state = True
        state.bulb_mode = BULB_MODE_NIGHT

        result = {}
        state.apply_state(result)

        self.assertEqual({
            "state": "ON",
            "color": {"b": 255, "g": 255, "r": 255},
            "bulb_mode": "night",
            "effect": 'night_mode',
        }, result)

    def test_apply_white(self):
        state = State()
        state.state = True
        state.bulb_mode = BULB_MODE_WHITE
        state.mireds = 370

        result = {}
        state.apply_state(result)

        self.assertEqual({
            "state": "ON",
            "color": {"b": 255, "g": 255, "r": 255},
            "bulb_mode": "white",
            "effect": 'white_mode',
            "color_temp": 370,
            "kelvin": 2700,
            "color_mode": "color_temp"
        }, result)

    def patched(self, *messages):
        state = State()
        for message in messages:
            state.patch(message)
        result = {}
        state.apply_state(result)
        return result

    def test_patch_color(self):
        result = self.patched({"state": "ON", "color": {"r": 255, "g": 0, "b": 0}})

        self.assertEqual("ON", result["state"])
        self.assertEqual("rgb", result["color_mode"])
        self.assertEqual({"r": 255, "g": 0, "b": 0}, result["color"])

    def test_patch_color_replaces_white(self):
        result = self.patched({"color_temp": 250}, {"color": {"r": 0, "g": 0, "b": 255}})

        self.assertEqual("rgb", result["color_mode"])
        self.assertEqual({"r": 0, "g": 0, "b": 255}, result["color"])
        self.assertNotIn("color_temp", result)

    def test_patch_near_white_color(self):
        result = self.patched({"color": {"r": 250, "g": 250, "b": 250}})

        self.assertEqual("color_temp", result["color_mode"])
        self.assertEqual(370, result["color_temp"])

    def test_patch_color_temp(self):
        result = self.patched({"color": {"r": 255, "g": 0, "b": 0}}, {"color_temp": 250})

        self.assertEqual("color_temp", result["color_mode"])
        self.assertEqual(251, result["color_temp"])

    def test_patch_brightness_uses_new_mode(self):
        result = self.patched(
            {"color_temp": 250, "brightness": 100},
            {"color": {"r": 255, "g": 0, "b": 0}, "brightness": 200},
        )
        # Values lose a little precision on the bulb's 0-100 scale.
        self.assertEqual(199, result["brightness"])

        result = self.patched(
            {"color_temp": 250, "brightness": 100},
            {"color": {"r": 255, "g": 0, "b": 0}, "brightness": 200},
            {"color_temp": 250},
        )
        self.assertEqual(99, result["brightness"])

    def test_patch_effects(self):
        result = self.patched({"effect": "3"})
        self.assertEqual("3", result["effect"])
        self.assertNotIn("color_mode", result)

        result = self.patched({"effect": "night_mode"})
        self.assertEqual("night_mode", result["effect"])
        self.assertNotIn("color_mode", result)

        result = self.patched({"effect": "white_mode"})
        self.assertEqual("white_mode", result["effect"])
        self.assertEqual("color_temp", result["color_mode"])

    def test_patch_leaves_night_mode(self):
        result = self.patched(
            {"color": {"r": 255, "g": 0, "b": 0}},
            {"effect": "night_mode"},
            {"color": {"r": 255, "g": 0, "b": 0}},
        )
        self.assertEqual("rgb", result["color_mode"])

    def test_patch_saturation_without_hue(self):
        result = self.patched({"saturation": 50})

        self.assertEqual(50, result["saturation"])
        self.assertNotIn("color", result)
        self.assertNotIn("color_mode", result)

    def test_patch_state_is_case_insensitive(self):
        self.assertEqual("ON", self.patched({"state": "on"})["state"])
        self.assertEqual("OFF", self.patched({"status": "off"})["state"])

    def test_unknown_state_not_reported(self):
        self.assertNotIn("state", self.patched({"brightness": 128}))
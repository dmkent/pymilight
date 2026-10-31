from pymilight.rgb_converter import rgb_to_hsv

# MiLight CCT bulbs range from 2700K-6500K, or ~370.3-153.8 mireds (warm to cool).
# Packets are sent with range 0-100.
# So we need to rescale 370 -> 153 onto 0 -> 100.
COLOR_TEMP_MAX_MIREDS = 370
COLOR_TEMP_MIN_MIREDS = 153
COLOR_TEMP_RANGE_MIREDS = COLOR_TEMP_MAX_MIREDS - COLOR_TEMP_MIN_MIREDS
RGB_WHITE_BOUNDARY = 40


def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))


def is_on(status):
    return str(status).lower() in ("on", "true")


def rgb_to_hue_saturation(red, green, blue):
    """Hue (0-360) and saturation (0-100), or None if the color is close to white."""
    if min(red, green, blue) > 256 - RGB_WHITE_BOUNDARY:
        return None

    hsv = rgb_to_hsv(red, green, blue)
    return int(round(hsv[0] * 360, 0)), int(round(hsv[1] * 100, 0))


def rescale(val, new_max, old_max):
    return round(val * (new_max / float(old_max)))


def mireds_to_white_val(mireds):
    val = (mireds - COLOR_TEMP_MIN_MIREDS)
    return constrain(int(round(val / float(COLOR_TEMP_RANGE_MIREDS) * 100.0, 0)), 0, 100)


def white_val_to_mireds(value):
    val = value / 100.0
    return int(round(COLOR_TEMP_RANGE_MIREDS * val + COLOR_TEMP_MIN_MIREDS, 0))


def kelvin_to_white_val(kelvin):
    return mireds_to_white_val(kelvin_to_mireds(kelvin))


def white_val_to_kelvin(value):
    return int(round(mireds_to_kelvin(white_val_to_mireds(value)), -1))


def kelvin_to_mireds(kelvin):
    return 1E6 / kelvin


def mireds_to_kelvin(mireds):
    return 1E6 / mireds
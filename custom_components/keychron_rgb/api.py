"""Keychron RGB adapter API"""

from urllib.request import Request, urlopen
from json import loads, dumps
from .const import PORT

def is_available(addr) -> bool:
    """Checks that the keyboard is connected and available for requests"""
    try:
        req = Request(f"http://{addr}:{PORT}/status")
        return loads(urlopen(req).read().decode("utf-8"))
    except Exception: # pylint: disable=broad-except
        pass
    return False

def apply_effect(addr, effect, color, brightness) -> bool:
    """Applies effect to keyboard"""
    try:
        payload = {
            "effect": effect,
            "color": "#%02x%02x%02x" % color, # pylint: disable=consider-using-f-string
            "brightness": brightness,
        }
        req = Request(f"http://{addr}:{PORT}/apply", method='POST',
            data=dumps(payload).encode("utf-8"))
        urlopen(req).read().decode("utf-8")
        return True
    except Exception:  # pylint: disable=broad-except
        pass
    return False

"""Support for DoHome RGB Lights"""
from logging import getLogger
from typing import (
    Callable,
    Optional,
    Final,
    Any,
    Tuple
)
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_HS_COLOR,
    ATTR_EFFECT,
    COLOR_MODE_HS,
    PLATFORM_SCHEMA,
    SUPPORT_EFFECT,
    LightEntity,
)
import homeassistant.util.color as color_util
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from .const import CONF_ADDR
from .api import apply_effect, is_available

# pylint: disable=unused-argument,too-many-instance-attributes

_LOGGER = getLogger(__name__)

effects = [
    "Static",
    "Keystroke light up",
    "Keystroke dim",
    "Sparkle",
    "Rain",
    "Random colors",
    "Breathing",
    "Spectrum cycle",
    "Ring gradient",
    "Vertical gradient",
    "Horizontal gradient / Rainbow wave",
    "Around edges",
    "Keystroke horizontal lines",
    "Keystroke tilted lines",
    "Keystroke ripples",
    "Sequence",
    "Wave line",
    "Tilted lines",
    "Back and forth",
]

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ADDR): cv.string
})

async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up DoHome light platform"""
    if CONF_ADDR in config:
        async_add_entities([
            KeychronRGB(hass, config[CONF_ADDR])
        ])

class KeychronRGB(LightEntity):
    """DoHome light entity"""

    # Constants attributes
    _attr_supported_color_modes: Final[set[str]] = {
        COLOR_MODE_HS,
    }
    _attr_color_mode = COLOR_MODE_HS
    # State values
    _attr_brightness: int = 255
    _attr_is_on: bool = True
    _attr_available: bool = False

    _attr_supported_features = SUPPORT_EFFECT
    _attr_effect_list = effects
    _attr_effect = effects[0]

    _rgb: Tuple[int, int, int] = (0, 0, 0)
    _addr: str

    def __init__(self, hass, addr: str):
        self._addr = addr
        self._hass = hass

    @property
    def hs_color(self) -> tuple[float, float]:
        """Return the color property."""
        return color_util.color_RGB_to_hs(*self._rgb)

    @property
    def unique_id(self) -> str:
        """Return the unique id of the device."""
        return "keychron_k3v2optical"

    async def async_update(self) -> None:
        """Check if keyboard is available"""
        await self._hass.async_add_executor_job(self.update_status)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        if ATTR_EFFECT in kwargs:
            self._attr_effect = kwargs[ATTR_EFFECT]
        if ATTR_HS_COLOR in kwargs:
            self._rgb = color_util.color_hs_to_RGB(*kwargs[ATTR_HS_COLOR])
        if ATTR_BRIGHTNESS in kwargs:
            self._attr_brightness = kwargs[ATTR_BRIGHTNESS]
        await self._hass.async_add_executor_job(self.apply_effect)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        apply_effect(self._addr, 128, (0, 0, 0), 0)
        self._attr_is_on = False

    def apply_effect(self):
        """Updates status"""
        apply_effect(
            self._addr,
            effects.index(self._attr_effect) + 1,
            self._rgb,
            self._attr_brightness
        )
        self._attr_is_on = True
        self.async_write_ha_state()

    def update_status(self):
        """Updates status"""
        self._attr_available = is_available(self._addr)
        self.async_write_ha_state()

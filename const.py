"""Use serial protocol of BenQ projector to obtain state of the projector."""
from __future__ import annotations

from typing import Final

from homeassistant.const import STATE_OFF, STATE_ON

CONF_BAUDRATE: Final = "baudrate"
CONF_WRITE_TIMEOUT: Final = "write_timeout"

DEFAULT_NAME: Final = "BenQ Projector"
DEFAULT_TIMEOUT: Final = 1
DEFAULT_WRITE_TIMEOUT: Final = 1
DEFAULT_BAUDRATE: Final = 115200

# Attributes
POWER_STATUS: Final = "Power Status"
CURRENT_SOURCE: Final = "Current Source"
LAMP_HOURS: Final = "Lamp Hours"
LAMP_MODE: Final = "Lamp Mode"
MODEL: Final = "Model"
SYSFW: Final = "System F/W"
TEMPERATURE: Final = "Temperature"

# Icon
ICON: Final = "mdi:projector"

# Commands known to the projector
CMD_DICT: Final[dict[str, str]] = {
    # Write
    STATE_ON: "\r*pow=on#\r",
    STATE_OFF: "\r*pow=off#\r",
    
    # Read
    POWER_STATUS: "\r*pow=?#\r",
    CURRENT_SOURCE: "\r*sour=?#\r",
    LAMP_HOURS: "\r*ltim=?#\r",
    LAMP_MODE: "\r*lampm=?#<\r",
    MODEL: "\r*modelname=?#\r",
    SYSFW: "\r*sysfwversion=?#\r",
    TEMPERATURE: "\r*tmp1=?#\r",
}
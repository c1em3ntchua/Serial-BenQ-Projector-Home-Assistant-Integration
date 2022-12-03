"""Use serial protocol of BenQ projector to obtain state of the projector."""
# Forked on top of the Acer projector integration! https://github.com/home-assistant/core/tree/dev/homeassistant/components/acer_projector
# Credits = TrianguloY, CloudBurst, Hikaru, YayMuffins
from __future__ import annotations

import logging
import re
from typing import Any

import serial
import voluptuous as vol

from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchEntity
from homeassistant.const import (
    CONF_FILENAME,
    CONF_NAME,
    CONF_TIMEOUT,
    STATE_OFF,
    STATE_ON,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import (
    CONF_BAUDRATE,
    CONF_WRITE_TIMEOUT,
    
    DEFAULT_NAME,
    DEFAULT_TIMEOUT,
    DEFAULT_WRITE_TIMEOUT,
    DEFAULT_BAUDRATE,
    
    POWER_STATUS,
    
    SOURCE_HDMI1,
    SOURCE_HDMI2,
    SOURCE_HDMI3,
    SOURCE_CURRENT,
    
    LAMP_HOURS,
    LAMP_MODE,
    
    MODEL,
    SYSFW,
    TEMPERATURE,
    
    ICON,
    CMD_DICT,
)

DEFAULT_BAUDRATE = 115200

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_FILENAME): cv.isdevice,
        vol.Optional(CONF_BAUDRATE, default=DEFAULT_BAUDRATE): cv.positive_int,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int,
        vol.Optional(
            CONF_WRITE_TIMEOUT, default=DEFAULT_WRITE_TIMEOUT
        ): cv.positive_int,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Connect with serial port and return BenQ Projector."""
    serial_port = config[CONF_FILENAME]
    baudrate = config[CONF_BAUDRATE]
    name = config[CONF_NAME]
    timeout = config[CONF_TIMEOUT]
    write_timeout = config[CONF_WRITE_TIMEOUT]

    add_entities([BenQSwitch(serial_port, baudrate, name, timeout, write_timeout)], True)


class BenQSwitch(SwitchEntity):
    """Represents an BenQ Projector as a switch."""
    _attr_icon = ICON

    def __init__(
        self,
        serial_port: str,
        baudrate: int,
        name: str,
        timeout: int,
        write_timeout: int,
    ) -> None:
        """Init of the BenQ projector."""
        self.ser = serial.Serial(
            port=serial_port, baudrate=baudrate, timeout=timeout, write_timeout=write_timeout
        )
        self._serial_port = serial_port
        self._baudrate = baudrate
        self._attr_name = name
        self._attributes = {
        	POWER_STATUS: STATE_UNKNOWN,
        	SOURCE_CURRENT: STATE_UNKNOWN,
            LAMP_HOURS: STATE_UNKNOWN,
            LAMP_MODE: STATE_UNKNOWN,
        	MODEL: STATE_UNKNOWN,
        	SYSFW: STATE_UNKNOWN,
        	TEMPERATURE: STATE_UNKNOWN,
        }

    def _write_read(self, msg: str) -> str:
        """Write to the projector and read the return."""
        ret = ""
        # Sometimes the projector won't answer for no reason or the projector
        # was disconnected during runtime.
        # This way the projector can be reconnected and will still work
        try:
            if not self.ser.is_open:
                self.ser.open()
            self.ser.reset_input_buffer()
            self.ser.write(msg.encode("utf-8"))
            # Size is an experience value there is no real limit.
            # AFAIK there is no limit and no end character so we will usually
            # need to wait for timeout
            self.ser.read_until(size=20)
            ret = self.ser.read_until(size=20).decode("ascii")
            #ret=self.ser.read(999).decode("ascii")


        except serial.SerialException:
            _LOGGER.error("Problem communicating with %s", self._serial_port)
        self.ser.close()
        return ret

    def _write_read_format(self, msg: str) -> str:
        """Write msg, obtain answer and format output."""
        # answers are formatted as ***\answer\r***
        awns = self._write_read(msg)
        if match := re.search(r"=(.+)#", awns):
            return match.group(1)
        return STATE_UNKNOWN

    def update(self) -> None:
        """Get the latest state from the projector."""
        awns = self._write_read_format(CMD_DICT[POWER_STATUS])
        if awns == "ON":
            self._attr_is_on = True
            self._attr_available = True
        elif awns == "OFF":
            self._attr_is_on = False
            self._attr_available = True
        else:
            self._attr_available = False

        for key in self._attributes:
            if msg := CMD_DICT.get(key):
                awns = self._write_read_format(msg)
                if (TEMPERATURE in key) and (awns.isnumeric()):
                    awns = str(float(awns) / 10)
                self._attributes[key] = awns
        self._attr_extra_state_attributes = self._attributes

    def turn_on(self, **kwargs: Any) -> None:
        """Turn the projector on."""
        msg = CMD_DICT[STATE_ON]
        self._write_read(msg)
        self._attr_is_on = True

    def turn_off(self, **kwargs: Any) -> None:
        """Turn the projector off."""
        msg = CMD_DICT[STATE_OFF]
        self._write_read(msg)
        self._attr_is_on = False

    def switch_source_hdmi1(self, **kwargs: Any) -> None:
        """Turn the projector off."""
        msg = CMD_DICT[SOURCE_HDMI1]
        self._write_read(msg)

    def switch_source_hdmi2(self, **kwargs: Any) -> None:
        """Turn the projector off."""
        msg = CMD_DICT[SOURCE_HDMI2]
        self._write_read(msg)

    def switch_source_hdmi3(self, **kwargs: Any) -> None:
        """Turn the projector off."""
        msg = CMD_DICT[SOURCE_HDMI3]
        self._write_read(msg)

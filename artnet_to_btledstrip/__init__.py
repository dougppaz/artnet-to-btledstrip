"""
artnet_to_btledstrip module
"""
from typing import (
    Type,
    List,
    Optional,
    Dict,
)
from stupidArtnet import StupidArtnetServer  # type: ignore[import-untyped]
from btledstrip import (
    BTLedStrip,
    Controller,
    MELKController,
)

CONTROLLERS: Dict[str, Type[Controller]] = {
    "melk": MELKController
}

class Exec:
    """
    Exec
    """
    @classmethod
    def load(cls, led_strip: "LEDStrip", data: dict) -> "Exec":
        """
        load Exec from data
        """
        attr = data.get("exec")
        assert attr
        return Exec(led_strip,
                    attr,
                    data.get("channels", {}))

    def __init__(self,
                 led_strip: "LEDStrip",
                 attr: str,
                 channels: Optional[dict] = None) -> None:
        self._led_strip = led_strip
        self._attr = attr
        self._channels = channels or {}
        self._current_kwargs: Dict[str, int] = {}

    @property
    def led_strip(self) -> "LEDStrip":
        """
        LEDStrip manager
        """
        return self._led_strip

    @property
    def attr(self) -> str:
        """
        attr
        """
        return self._attr

    @property
    def channels(self) -> Dict[str, int]:
        """
        channels map
        """
        return self._channels

    def next_kwargs(self) -> Dict[str, int]:
        """
        build next kwargs
        """
        return dict(map(lambda item: (item[0],
                                      self.led_strip.dmx.value(item[1]),),
                        self.channels.items()))

    async def do(self, force: bool = False) -> None:
        """
        exec btstripline commands
        """
        exec_fn = getattr(self.led_strip.bt.exec, self.attr)
        next_kwargs = self.next_kwargs()
        if force or next_kwargs != self._current_kwargs:
            await exec_fn(**next_kwargs)
            self._current_kwargs = next_kwargs

class Mode:
    """
    Mode
    """
    @classmethod
    def load(cls, led_strip: "LEDStrip", data: dict) -> "Mode":
        """
        load Mode from data
        """
        until = data.get("until")
        assert isinstance(until, int)
        return Mode(led_strip,
                    until,
                    list(map(lambda exec_data: Exec.load(led_strip, exec_data),
                             data.get("execs", []))))

    def __init__(self,
                 led_strip: "LEDStrip",
                 until: int,
                 execs: List[Exec]) -> None:
        self._led_strip = led_strip
        self._until = until
        self._execs = execs

    @property
    def led_strip(self) -> "LEDStrip":
        """
        LEDStrip manager
        """
        return self._led_strip

    @property
    def until(self) -> int:
        """
        until
        """
        return self._until

    @property
    def execs(self) -> List[Exec]:
        """
        execs list
        """
        return self._execs

class LEDStrip:
    """
    LEDStrip manager
    """
    @classmethod
    def load(cls, dmx: "DMXUniverseListener", data: dict) -> "LEDStrip":
        """
        load LEDStrip instance from data
        """
        controller_class = CONTROLLERS.get(data.get("controller", "unset"))
        assert controller_class
        mac_address = data.get("mac_address")
        assert mac_address
        led_strip = LEDStrip(dmx,
                             controller_class,
                             mac_address,
                             data.get("mode_channel", 1))
        led_strip.modes = list(map(lambda mode_data: Mode.load(led_strip, mode_data),
                                   data.get("modes", [])))
        return led_strip

    def __init__(self,  # pylint: disable=R0913
                 dmx: "DMXUniverseListener",
                 controller_class: Type[Controller],
                 mac_address: str,
                 mode_channel: int = 1,
                 modes: Optional[List[Mode]] = None) -> None:
        self._dmx = dmx
        self._controller_class = controller_class
        self._mac_address = mac_address
        self._mode_channel = mode_channel
        self.modes: List[Mode] = modes or []
        self._bt: Optional[BTLedStrip] = None
        self._current_mode: Optional[Mode] = None

    @property
    def dmx(self) -> "DMXUniverseListener":
        """
        DMXUniverseListener instance
        """
        return self._dmx

    @property
    def controller_class(self) -> Type[Controller]:
        """
        controller class
        """
        return self._controller_class

    @property
    def mac_address(self) -> str:
        """
        LED Strip controller mac address
        """
        return self._mac_address

    @property
    def mode_channel(self) -> int:
        """
        mode channel
        """
        return self._mode_channel

    @property
    def bt(self) -> BTLedStrip:
        """
        BTLedStrip instance
        """
        if not self._bt:
            controller = self.controller_class()
            self._bt = BTLedStrip(controller, self.mac_address)
        assert self._bt
        return self._bt

    async def tick(self) -> None:
        """
        tick
        """
        mode_value = self.dmx.value(self.mode_channel)
        for mode in self.modes:
            if mode.until >= mode_value:
                mode_changed = False
                if self._current_mode != mode:
                    self._current_mode = mode
                    mode_changed = True
                for ex in mode.execs:
                    await ex.do(force=mode_changed)
                break

class DMXUniverseListener:
    """
    DMX universe listener with Art-Net server
    """
    _artnet_server: StupidArtnetServer
    _values: List[int] = []

    def __init__(self,
                 artnet_server: Optional[StupidArtnetServer] = None,
                 universe: int = 0) -> None:
        self._artnet_server = artnet_server or StupidArtnetServer()
        self._listener_id = self._artnet_server.register_listener(
            universe,
            callback_function=self.callback_function
        )

    def callback_function(self, values: List[int]) -> None:
        """
        calls callback function on receive new values
        """
        self._values = values

    def value(self, channel: int) -> int:
        """
        get dmx channel value
        """
        return self._values[channel - 1]
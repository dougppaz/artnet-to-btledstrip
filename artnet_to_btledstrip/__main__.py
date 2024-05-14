"""
usage: python -m artnet_to_btledstrip -h
"""
import asyncio
import argparse
import logging
from typing import (
    Optional,
    Any
)
from yaml import (
    load,
    CLoader as Loader,
)
from artnet_to_btledstrip import (
    LEDStrip,
    DMXUniverseListener,
)

logger = logging.getLogger(__name__)

class LEDStripAction(argparse.Action):
    """
    led_strip_config_file to led_strip action
    """
    def __call__(self,
                 _: argparse.ArgumentParser,
                 namespace: argparse.Namespace,
                 values: Any,
                 option_string: Optional[str] = None) -> None:
        with open(values, encoding="utf-8") as config_file:
            data = load(config_file, Loader=Loader)
            led_strip = LEDStrip.load(namespace.dmx, data)
            setattr(namespace, "led_strip", led_strip)

async def main(led_strip: LEDStrip):
    """
    main
    """
    async with led_strip.bt:
        while True:
            try:
                await led_strip.tick()
            except Exception as e:  # pylint: disable=W0718
                logger.exception(e)
            await asyncio.sleep(.05)

parser = argparse.ArgumentParser(prog="artnet to brledstrip")
parser.add_argument("led_strip_config_file",
                    action=LEDStripAction)

if __name__ == "__main__":
    dmx = DMXUniverseListener()
    args = parser.parse_args(namespace=argparse.Namespace(dmx=dmx))
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main(args.led_strip))

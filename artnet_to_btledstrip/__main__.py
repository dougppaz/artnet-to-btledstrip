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
    DMXServer,
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
            led_strip = LEDStrip.load(data)
            setattr(namespace, "led_strip", led_strip)

async def main(led_strip: LEDStrip, universe: int):
    """
    main
    """
    dmx_server = DMXServer()
    async with dmx_server.listen(universe) as dmx, led_strip.bt:
        while True:
            try:
                await led_strip.tick(dmx)
            except Exception as e:  # pylint: disable=W0718
                logger.exception(e)

parser = argparse.ArgumentParser(prog="artnet to brledstrip")
parser.add_argument("led_strip_config_file",
                    action=LEDStripAction)
parser.add_argument("--universe",
                    type=int,
                    default=1)

if __name__ == "__main__":
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main(args.led_strip, args.universe))

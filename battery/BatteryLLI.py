#!/usr/bin/env python3

import asyncio
import logging
try:
    import RPi.GPIO as gpio
except ModuleNotFoundError:
    logging.error("RPi gpio backend not found")
    import hevgpio as gpio
import copy
from CommsCommon import BatteryFormat

# Set up logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.DEBUG)

class BatteryLLI:
    def __init__(self, timeout=1):
        super().__init__()
        self._timeout = timeout
        self._pins = {"bat"      :  5,
                      "ok"       :  6,
                      "alarm"    : 12,
                      "rdy2buf"  : 13,
                      "bat85"    : 19,
                      "prob_elec":  7}
        self._payload = BatteryFormat()
        try:
            if gpio.DUMMY:
                self._payload.dummy = True
        except:
            self._payload.dummy = False

        gpio.setmode(gpio.BCM)
        for pin in self._pins:
            gpio.setup(self._pins[pin], gpio.IN, pull_up_down=gpio.PUD_DOWN)
            
    async def main(self) -> None:
        while True:
            await asyncio.sleep(self._timeout)
            try:
                for pin in self._pins:
                    setattr(self._payload, pin, gpio.input(self._pins[pin]))
                logging.debug(self._payload)
            except:
                logging.error("Failed gpio data save")

if __name__ == "__main__":
    try:
        # schedule async tasks
        loop = asyncio.get_event_loop()

        # setup serial devices
        battery = BatteryLLI()

        asyncio.gather(battery.main(), return_exceptions=True)
        loop.run_forever()
    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        logging.info("Closing LLI")
    finally:
        loop.close()

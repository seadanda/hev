#!/usr/bin/env python3

import asyncio
import RPi.GPIO as gpio

# Set up logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.INFO)

class BatteryLLI:
    def __init__(self, loop, timeout=1):
        super().__init__()
        self._timeout = timeout
        self._pins = {"bat"     :  5,
                      "ok"      :  6,
                      "alarm"   : 12,
                      "rdy2bif" : 13,
                      "bat85"   : 19}

        gpio.setmode(gpio.BCM)
        for pin in self._pins:
            gpio.setup(self._pins[pin], gpio.IN)
            self._res[pin] = 0
            
    async def getValues(self):
        await asyncio.sleep(self._timeout)
        for pin in self._pins:
            self._res[pin] = gpio.input(self._pins[pin])
        logging.info(f"Battery: {res}")
    
    async def main(self) -> None:
        results = self.getValues()  # NativeUI broadcast
        tasks = [results]

        await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == "__main__":
    try:
        # schedule async tasks
        loop = asyncio.get_event_loop()

        # setup serial devices
        battery = BatteryLLI(loop)

        asyncio.gather(battery.main(), return_exceptions=True)
        loop.run_forever()
    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        logging.info("Closing LLI")
    finally:
        loop.close()
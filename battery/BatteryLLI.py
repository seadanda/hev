#!/usr/bin/env python3

import asyncio
import logging
try:
    import RPi.GPIO as gpio
except ModuleNotFoundError:
    logging.warning("RPi gpio backend not found, will use dummy")
    import hevgpio as gpio
import copy
from CommsCommon import BatteryFormat

# Set up logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.DEBUG)

class BatteryLLI:
    def __init__(self, timeout=1, dump=False):
        super().__init__()
        self._timeout = timeout
        self._pins = {"bat"      :  5,
                      "ok"       :  6,
                      "alarm"    : 12,
                      "rdy2buf"  : 13,
                      "bat85"    : 19,
                      "prob_elec":  7}
        self._dump = dump
        self._dumpfile = "share/battdump.dict"
        if self._dump:
            with open(self._dumpfile, 'w'):
                pass
        self._dummy = False
        self.queue = asyncio.Queue()

        try:
            if gpio.DUMMY:
                self._dummy = True
        except:
            pass

        gpio.setmode(gpio.BCM)
        for pin in self._pins:
            gpio.setup(self._pins[pin], gpio.IN, pull_up_down=gpio.PUD_DOWN)
            
    async def main(self) -> None:
        while True:
            await asyncio.sleep(self._timeout)
            payload = BatteryFormat(dummy=self._dummy)
            try:
                for pin in self._pins:
                    setattr(payload, pin, gpio.input(self._pins[pin]))
                self.queue.put_nowait(payload)
            except asyncio.queues.QueueFull:
                try:
                    self.queue.get_nowait()
                    self.queue.task_done()
                    self.queue.put_nowait(payload)
                except Exception as e:
                    # Queue is being written from somewhere else. won't get here
                    logging.error(e)
                    continue
            except Exception:
                logging.error("Failed gpio data save")
                continue
            finally:
                logging.debug(payload)
                if self._dump == True:
                    with open(self._dumpfile, 'a') as f:
                        f.write(f"{payload.getDict()}\n")
    
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

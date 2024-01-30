import asyncio
import multiprocessing
import sys
import time

from xknx import XKNX
from xknx.devices import Switch



class Light:
    lights = []

    def __init__(self):
        self.address = "0/0/" + str(len(Light.lights) + 1)
        self.status_address = "0/1/" + str(len(Light.lights) + 1)
        # state is a lock
        self._state_lock = multiprocessing.Queue(1)
        self.state = False

        self._stop_light_off_event = multiprocessing.Event()
        self._light_off_process = multiprocessing.Process(target=self.light_off_timer)
        self._light_off_process.start()

        Light.lights.append(self)
        # The light is switched off at the start
        asyncio.run(self.lights_update(0))


    def light_on(self):
        """switch on the light if the light is off, if the timer is still running, set the state as True"""
        if not self._state_lock.empty():
            state = self._state_lock.get()
            if not state:
                asyncio.run(self.lights_update(1))
        else:
            # The queue is no longer empty so the update of the timer is nullified
            self._state_lock.put(True)

    def light_off(self):
        """if the light is on, starts a 3 seconds timer before switching off the light """
        if not self._state_lock.empty():
            state = self._state_lock.get()
            if state:
                # Starts timer
                self._stop_light_off_event.clear()

    def light_off_timer(self):
        """3 seconds timer that starts if the event is clear. After the execution is idle"""
        while True:
            while not self._stop_light_off_event.is_set():
                time.sleep(5)
                asyncio.run(self.lights_update(0))
                # Becomes idle
                self._stop_light_off_event.set()

    async def lights_update(self, new_state):
        """turns the light if the queue is empty. The queue is not empty when the switching off has to be stopped"""
        try:
            async with XKNX() as xknx:
                s = Switch(xknx, "switch", self.address, self.status_address)
                if self._state_lock.empty():
                    # Works as normal
                    if new_state:
                        await s.set_on()
                        self._state_lock.put(True)
                        print(f"{self.address}", "on")
                    else:
                        await s.set_off()
                        self._state_lock.put(False)
                        print(f"{self.address}", "off")
                else:
                    # Do nothing, this happens only when the switching off has to be stopped
                    pass



        except Exception as e:
            print("xknx Error:", e)
            sys.exit()



    @classmethod
    def clear_lights(cls):
        cls.lights = []



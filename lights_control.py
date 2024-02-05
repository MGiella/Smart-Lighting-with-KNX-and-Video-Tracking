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

        self._stop_light_off_event = multiprocessing.Event()
        self._state = multiprocessing.Event()

        self._light_off_process = multiprocessing.Process(target=self.light_off_timer)
        self._light_off_process.daemon = True
        self._light_off_process.start()

        Light.lights.append(self)
        # The light is switched off at the start
        asyncio.run(self.lights_update(0))

    @property
    def state(self):
        """state is on or off """
        if self._state.is_set():
            return "ON"
        else:
            return "OFF"

    @state.setter
    def state(self, value):
        """if the state is set to True, sets the event"""
        if value:
            self._state.set()
        else:
            self._state.clear()

    def light_on(self):
        """switch on the light if the light is off, if the timer is still running, set the state"""
        if self.state == "OFF":
            asyncio.run(self.lights_update(1))
        elif not self._stop_light_off_event.is_set():
            self._stop_light_off_event.set()


    def light_off(self):
        """if the light is on, starts a 3 seconds timer before switching off the light """
        if self.state == "ON":
            #starts timer
            self._stop_light_off_event.clear()

    def light_off_timer(self):
        """8 seconds timer that starts if the event is cleared.
         After each second check if the light tried to be switched on"""
        while True:
            i=0
            # if the event was cleared
            while not self._stop_light_off_event.is_set():
                time.sleep(1)
                i+=1
                # if the light wasn't requested to be switched on and 8 seconds have passed
                if not self._stop_light_off_event.is_set() and i==8:
                    asyncio.run(self.lights_update(0))
                    # Becomes idle
                    self._stop_light_off_event.set()
                    i=0

    async def lights_update(self, new_state):
        """turns the light if the queue is empty. The queue is not empty when the switching off has to be stopped"""
        try:
            async with XKNX() as xknx:
                s = Switch(xknx, "switch", self.address, self.status_address)
                if new_state:
                    await s.set_on()
                    print(f"{self.address}", "on")
                    self.state = True
                else:
                    await s.set_off()
                    print(f"{self.address}", "off")
                    self.state = False

        except Exception as e:
            print("xknx Error:", e)
            sys.exit()

    @classmethod
    def clear_lights(cls):
        cls.lights = []

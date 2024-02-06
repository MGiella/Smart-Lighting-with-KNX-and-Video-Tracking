import multiprocessing

import requests
from requests.auth import HTTPBasicAuth
from PTZ.camera import Camera


class CameraController:
    def __init__(self, cam: Camera):
        self._cam = cam
        self._speed = 65
        self.__url = 'http://' + self._cam._ip + '/cgi-bin/hi3510/ptzctrl.cgi'

        self.jobs = multiprocessing.JoinableQueue()
        self.createProcesses(self.jobs, 2)

    def createProcesses(self, jobs, concorrenza):
        """the movements are manages concurrently by requests"""
        for _ in range(concorrenza):
            proc = multiprocessing.Process(None, target=self._perform_move, args=(jobs,))
            proc.daemon = True
            proc.start()

    def stop(self):
        params = {
            '-act': 'stop'
        }
        self.jobs.put(params)

    def move_right(self, continuous=True):
        step = 0
        if not continuous:
            step = 1

        params = {
            '-step': str(step),
            '-act': 'right',
            '-speed': str(self._speed)
        }
        self.jobs.put(params)

    def move_left(self, continuous=True):
        step = 0
        if not continuous:
            step = 1

        params = {
            '-step': str(step),
            '-act': 'left',
            '-speed': str(self._speed)
        }
        self.jobs.put(params)

    def move_up(self, continuous=True):
        step = 0
        if not continuous:
            step = 1

        params = {
            '-step': str(step),
            '-act': 'up',
            '-speed': str(self._speed)
        }
        self.jobs.put(params)

    def move_down(self, continuous=True):
        step = 0
        if not continuous:
            step = 1

        params = {
            '-step': str(step),
            '-act': 'down',
            '-speed': str(self._speed)
        }
        self.jobs.put(params)

    def zoom_in(self, continuous=True):
        step = 0
        if not continuous:
            step = 1

        params = {
            '-step': str(step),
            '-act': 'zoomin',
            '-speed': str(self._speed)
        }
        self.jobs.put(params)

    def zoom_out(self, continuous=True):
        step = 0
        if not continuous:
            step = 1

        params = {
            '-step': str(step),
            '-act': 'zoomout'
        }
        self.jobs.put(params)

    def _perform_move(self, jobs):
        """perform movement specified by the parameters in the jobs queue"""
        while True:
            try:
                params = jobs.get()
                requests.get(self.__url, params, auth=HTTPBasicAuth(self._cam._user, self._cam._password))
            except Exception as e:
                print(e)

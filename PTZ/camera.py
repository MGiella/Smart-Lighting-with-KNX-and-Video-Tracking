import sys

import requests
from requests.auth import HTTPBasicAuth


class Camera:
    def __init__(self, ip, user, password):
        self._ip = ip
        self._user = user
        self._password = password
        self.MINSPEED = 1
        self.MAXSPEED = 65


        # Check if the camera can connect via http
        url = 'http://' + self._ip + '/cgi-bin/hi3510/param.cgi?cmd=getnetattr'
        try:
            requests.get(url, auth=HTTPBasicAuth(self._user, self._password))
        except Exception as ex:
            print(ex)
            sys.exit()

    def __str__(self):
        return str({'IP': self._ip,
                    'user': self._user,
                    'password': self._password})

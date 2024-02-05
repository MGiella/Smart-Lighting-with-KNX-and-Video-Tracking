import requests
from requests.auth import HTTPBasicAuth

log = 'LOG(amera.py): '


class Camera:
    def __init__(self, ip, user, password):
        self._ip = ip
        self._user = user
        self._password = password
        self.MINSPEED = 1
        self.MAXSPEED = 65

        url = 'http://' + self._ip + '/cgi-bin/hi3510/param.cgi?cmd=getnetattr'
        try:
            response = requests.get(url, auth=HTTPBasicAuth(self._user, self._password))
            print(log + str(response.status_code))
        except Exception as ex:
            print(ex)

    # Stampa della telecamera
    def __str__(self):
        return str({'IP': self._ip,
                    'user': self._user,
                    'password': self._password})

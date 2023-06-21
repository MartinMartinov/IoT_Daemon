# Other
import json
import requests
import urllib3
from math import atan

### Access the Somneo ###
class somneoLight():
    def connect(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        inputs = json.load(open("/home/martinov/IoT_Daemon/somneo.json"))
        self.host = inputs['IP']
        
        url  = "https://" + self.host + "/upnp/description.xml"

        try:
            response = requests.get(url, verify=False, timeout=20)
        except requests.Timeout:
            print("Connection to Somneo timed out.")
            raise
        except requests.RequestException:
            print("Error connecting to Somneo.")
            raise

        if not response.content:
            print("Did not get any content when requesting device data.")
            return

    def set_alarm(self, hour, minute):
        # Default alarm settings dict
        settings = {}
        settings['prfnr'] = 1 # Alarm number from 1 to 15
        settings['prfen'] = True # True when alarm is on, False when it isn't
        settings['prfvs'] = True # Hide on Sleep Mapper app
        settings['pname'] = "Python"
        settings['ayear'] = 0
        settings['amnth'] = 0
        settings['alday'] = 0
        settings['daynm'] = 254 # First seven bits are the 7 days of the week
        settings['almhr'] = hour
        settings['almmn'] = minute
        settings['ctype'] = 0 # Light curve type: sunny day (0), island red (1), nordic white (2)
        settings['curve'] = 25 # Light level (0 - 25, 0 is no light)
        settings['durat'] = 5 # Duration in minutes (5 - 40)
        settings['snddv'] = "fmr"
        settings['sndch'] = "3"  # Sound channel (3 is radio)
        settings['sndlv'] = 25 # Sound level out of 25
        settings['sndss'] = 0
        settings['pwrsz'] = 0 # Power snooze?
        settings['pszhr'] = 0 # Power snooze hours?
        settings['pszmn'] = 0 # Power snooze minutes
        
        self.put_alarm_settings(settings)

    def unset_alarm(self):
        # Default alarm settings dict
        settings = {}
        settings['prfnr'] = 1 # Alarm number from 1 to 15
        settings['prfen'] = False # True when alarm is on, False when it isn't
        settings['prfvs'] = True # Hide on Sleep Mapper app
        settings['pname'] = "Python"
        settings['ayear'] = 0
        settings['amnth'] = 0
        settings['alday'] = 0
        settings['daynm'] = 0 # First seven bits are the 7 days of the week
        settings['almhr'] = hour
        settings['almmn'] = minute
        settings['ctype'] = 0 # Light curve type: sunny day (0), island red (1), nordic white (2)
        settings['curve'] = 25 # Light level (0 - 25, 0 is no light)
        settings['durat'] = 5 # Duration in minutes (5 - 40)
        settings['snddv'] = "fmr"
        settings['sndch'] = "3" # Sound channel (3 is radio)
        settings['sndlv'] = 25 # Sound level out of 25
        settings['sndss'] = 0
        settings['pwrsz'] = 0 # Power snooze?
        settings['pszhr'] = 0 # Power snooze hours?
        settings['pszmn'] = 0 # Power snooze minutes
        
        self.put_alarm_settings(settings)
        
    def put_alarm_settings(self, settings):
        args = {}
        url  = "https://" + self.host + "/di/v1/products/1/wualm/prfwu"
        args['data'] = json.dumps(settings)
        args['headers'] = {"Content-Type": "application/json"}

        #print(settings)
        try:
            response = requests.put(url, verify=False, timeout=20, **args)
        except requests.Timeout:
            print("Connection to Somneo timed out.")
            raise
        except requests.RequestException:
            print("Error connecting to Somneo.")
            raise

        try:
            response = json.loads(str(response.content)[2:-1])
        except:
            print(f"Did not get a proper response from Somneo.")
            return

        if response['prfen']:
            print(f"Somneo alarm set for \033[91m{response['almhr']:02d}\033[39m:\033[91m{response['almmn']:02d}\033[39m")#\
                #f":{response['almmn']}.\n\t{response}")
        else:
            print(f"Somneo alarm turned off.")
        
    def get_alarm_settings(self, alarm):
        args = {}
        settings = {}
        settings['prfnr'] = alarm # Alarm number from 1 to 15

        url  = "https://" + self.host + "/di/v1/products/1/wualm"
        args['data'] = json.dumps(settings)
        args['headers'] = {"Content-Type": "application/json"}

        try:
            response = requests.put(url, verify=False, timeout=20, **args)
        except requests.Timeout:
            print("Connection to Somneo timed out.")
            raise
        except requests.RequestException:
            print("Error connecting to Somneo.")
            raise

        print(response.content)
        
    def get_wt_temperature(self):
        url  = "https://" + self.host + "/di/v1/products/1/wusrd"

        try:
            response = requests.get(url, verify=False, timeout=20)
        except requests.Timeout:
            print("Connection to Somneo timed out.")
            raise
        except requests.RequestException:
            print("Error connecting to Somneo.")
            raise

        sensor_data = json.loads(response.content)
        try:
            T, rh = sensor_data['mstmp'], sensor_data['msrhu']
        except:
            return -1000

        return T*atan(0.152*(rh+8.3136)**(0.5))+atan(T+rh)-atan(rh-1.6763)+0.00391838*(rh)**(1.5)*atan(0.0231*rh)-4.686

    def get_temperature(self):
        url  = "https://" + self.host + "/di/v1/products/1/wusrd"

        try:
            response = requests.get(url, verify=False, timeout=20)
        except requests.Timeout:
            print("Connection to Somneo timed out.")
            raise
        except requests.RequestException:
            print("Error connecting to Somneo.")
            raise

        sensor_data = json.loads(response.content)
        try:
            return sensor_data['mstmp']
        except:
            return -1000

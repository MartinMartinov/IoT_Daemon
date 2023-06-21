# Other
import datetime
import json
import time
import hashlib
import hmac
import base64
import uuid
import requests

# Set up schedule

### Access the SwitchBot devices ###
class switchBot():
    def connect(self):
        # Set up SwitchBot device
        inputs = json.load(open("/home/martinov/IoT/switchbot.json"))
        token  = inputs['token']
        secret = inputs['secret']
        self.blinds = inputs['blinds']
        self.hubs   = inputs['hubs']
        self.acs    = inputs['acs']
        
        # Setup API
        self.url = "https://api.switch-bot.com/v1.1/"
        
        # Declare empty header dictionary
        self.apiHeader = {}
        
        # Generate nonce
        nonce = uuid.uuid4()
        t = int(round(time.time() * 1000))
        string_to_sign = f"{token}{t}{nonce}"

        string_to_sign = bytes(string_to_sign, "utf-8")
        secret = bytes(secret, "utf-8")

        sign = base64.b64encode(hmac.new(secret, msg=string_to_sign, digestmod=hashlib.sha256).digest())

        # Build api header JSON
        self.apiHeader['Authorization']=token
        self.apiHeader['Content-Type']="application/json"
        self.apiHeader['charset']="utf8"
        self.apiHeader['t']=str(t)
        self.apiHeader['sign']=sign
        self.apiHeader['nonce']=str(nonce)
        
        # Get blinds position
        try:
            response = requests.get(
                self.url+"devices",
                headers=self.apiHeader,
                timeout=20
            )
        except requests.Timeout:
            print("Connection to SwitchBot timed out.")
            raise
        except requests.RequestException:
            print("Error connecting to SwitchBot.")
            raise

        try:
            response = json.loads(str(response.content)[2:-1])
        except:
            print(f"Did not get a proper response from SwitchBot.")
            return

        foundBlinds = []
        for device in response['body']['deviceList']:
            if 'deviceType' in device:
                if device['deviceType'] == "Blind Tilt":
                    foundBlinds.append(device['deviceId'])

        for blind in self.blinds:
            if blind not in foundBlinds:
                print("Did not get all expected blinds in response.")
                return

        foundHubs = []
        for device in response['body']['deviceList']:
            if 'deviceType' in device:
                if device['deviceType'] == "Hub Mini":
                    foundHubs.append(device['deviceId'])

        for hub in self.hubs:
            if hub not in foundHubs:
                print("Did not get all expected hubs in response.")
                return

        foundAcs = []
        for device in response['body']['infraredRemoteList']:
            if 'remoteType' in device:
                if device['deviceName'] == "Air Conditioner":
                    foundAcs.append(device['deviceId'])

        for ac in self.acs:
            if ac not in foundAcs:
                print("Did not get all expected acs in response.")
                return

    def set_blinds(self, command):
        if command == "open":
            command = "fullyOpen"
        elif command =="close":
            command = "closeDown"

        for blind in self.blinds:
            url     = self.url + f"devices/{blind}/commands"
            payload = {
                'command'    : command,
                'parameter'  : "default",
                'commandType': "command"
            }

            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers=self.apiHeader,
                    timeout=20
                )
            except requests.Timeout:
                print("Connection to SwitchBot timed out.")
                raise
            except requests.RequestException:
                print("Error connecting to SwitchBot.")
                raise

            try:
                response = json.loads(str(response.content)[2:-1])
            except:
                print("Did not get a proper response from SwitchBot.")
                return
            
            if 'message' not in response:
                print("Received incorrect response.")
                return
            else:
                if response['message'] != "success":
                    print("Did not receive a success response.")
                    return

            print(f"Succesfully set SwitchBot to {command}.")
            #print(response)

    def set_ac(self, command):
        if command == "on":
            command = "turnOn"
        elif command =="off":
            command = "turnOff"

        for ac in self.acs:
            url     = self.url + f"devices/{ac}/commands"
            payload = {
                'command'    : command,
                'parameter'  : "default",
                'commandType': "command"
            }

            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers=self.apiHeader,
                    timeout=20
                )
            except requests.Timeout:
                print("Connection to SwitchBot timed out.")
                raise
            except requests.RequestException:
                print("Error connecting to SwitchBot.")
                raise

            try:
                response = json.loads(str(response.content)[2:-1])
            except:
                print("Did not get a proper response from SwitchBot.")
                print(response)
                return
            
            if 'message' not in response:
                print("Received incorrect response.")
                print(response)
                return
            else:
                if response['message'] != "success":
                    print("Did not receive a success response.")
                    print(response)
                    return

            print(f"Succesfully set AC to {command}.")
            #print(response)
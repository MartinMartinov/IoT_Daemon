#!/usr/bin/python

from google_cal     import GoogleCal
from google_weather import get_weather_data
from somneo_bot     import somneoLight
from switchbot_bot  import switchBot

import datetime
import pytz
import time
import ssl

# Colours
def red(string: str):
    return "\033[91m"+string+"\033[0m"
def yellow(string: str):
    return "\033[93m"+string+"\033[0m"
def blue(string: str):
    return "\033[94m"+string+"\033[0m"

# Settings for alarms
BIKE_WEATHER          = ["sunny", "cloudy"]  # Google weather results
WORK_TRAVEL_TIME      = 75  # minutes
WORK_BIKE_TRAVEL_TIME = 90  # minutes
WORK_BIKE_TEMP_THRESH = 12  # minutes
BLINDS_CLOSE_HOUR     = 23  # hours
CHECK_INTERVAL        = 600 # seconds

# Settings for AC
WB_TEMP_THRESH = 16 # Wet bulb temperature threshold for AC in celsius
TEMP_THRESH    = 22 # Dry bulb temperature threshold for AC in celsius

# Variables
last_day     = None
alarm_hour   = 25
alarm_minute = 61
blind_state  = "close"
ac_state     = "off"
ac_count     = 0

def set_todays_alarms():
    calendar = GoogleCal()
    calendar.connect()
    times = calendar.get_start_today(['Alarm','Work'])

    if times:
        # Sort by times and pull the first item
        thing, time = list(times.keys())[0], list(times.values())[0] 
        for key, value in times.items():
            if time > value:
                thing, time = key, value

        # Alarm needed today
        print(f"We have {yellow(thing)} at {red(format(time.hour,'02d'))}:{red(format(time.minute,'02d'))}")
        
        # Shift time for work events
        if thing == "Work":
            weather = get_weather_data()
            outside = weather['next_days'][0]['weather'].split(" ")[-1].lower()
            lows    = weather['next_days'][0]['min_temp']
            print(f"We have {yellow(weather['next_days'][0]['weather'])} with a low of {blue(lows)}")
            if outside in BIKE_WEATHER and int(lows) > WORK_BIKE_TEMP_THRESH:
                print(f"Giving {red(str(WORK_BIKE_TRAVEL_TIME))} minute bike riding time.")
                time = time - datetime.timedelta(minutes=WORK_BIKE_TRAVEL_TIME)
            else:
                print(f"Giving {red(str(WORK_TRAVEL_TIME))} minute car travel time.")
                time = time - datetime.timedelta(minutes=WORK_TRAVEL_TIME)
        print(f"Setting alarms for {red(format(time.hour,'02d'))}:{red(format(time.minute,'02d'))}")

        # Set somneo alarm
        somneo = somneoLight()
        somneo.connect()
        somneo.set_alarm(time.hour, time.minute)
        
        return time.hour, time.minute
    else:
        # Turn off the somneo
        somneo = somneoLight()
        somneo.connect()
        somneo.unset_alarm()
        return 24, 1

def close_blinds():
    global blind_state
    switch = switchBot()
    try:
        switch.connect()
        switch.set_blinds("close")
        blind_state = "close"
    except HttpAccessTokenRefreshError:
        pass # Hope it works next time

def open_blinds():
    global blind_state
    switch = switchBot()
    try:
        switch.connect()
        switch.set_blinds("open")
        blind_state = "open"
    except HttpAccessTokenRefreshError:
        pass # Hope it works next time

def check_AC():
    global ac_state
    global ac_count
    # If its night and hot, turn on AC for at least 3 intervals to get below threshold
    # Get wet bulb temperature
    somneo = somneoLight()
    somneo.connect()
    try:
        temp = somneo.get_wt_temperature(); check_temp = WB_TEMP_THRESH
        print(f"Wet bulb temperature is {blue(format(temp,'2.2f'))} degrees at {red(format(now.hour,'02d'))}:{red(format(now.minute,'02d'))}")
        #temp = somneo.get_temperature(); check_temp = TEMP_THRESH
        #print(f"Temperature is {blue(format(temp,'2.2f'))} degrees at {red(format(now.hour,'02d'))}:{red(format(now.minute,'02d'))}")
    except ssl.SSLEOFError:
        print(f"Failed to connect at {red(format(now.hour,'02d'))}:{red(format(now.minute,'02d'))}, assuming same temperature")
    
    # Check if the AC is needed, if so, turn it on
    if check_temp < temp and ac_state != "on":
        print(f"{blue(format(temp,'2.2f'))} is above {blue(format(check_temp,'2f'))} at {red(format(now.hour,'02d'))}:{red(format(now.minute,'02d'))}, starting up AC")
        switch = switchBot()
        try:
            switch.connect()
            switch.set_ac("on")
            ac_state = "on"
            ac_count = 0
        except HttpAccessTokenRefreshError:
            pass # Hope it works next time
    elif check_temp < temp and ac_state != "off" and ac_count:
        print(f"{blue(format(temp,'2.2f'))} is above {blue(format(check_temp,'2f'))}, resetting cycle count")
        ac_count = 0
    elif check_temp > temp and ac_count < 3 and ac_state != "off":
        print(f"{blue(format(temp,'2.2f'))} is below {blue(format(check_temp,'2f'))} counting {yellow(format(3-ac_count),'0d')} more cycles before turning off AC")
        ac_count = ac_count + 1
    elif check_temp > temp and ac_state != "off":
        print(f"{blue(format(temp,'2.2f'))} is below {blue(format(check_temp,'2f'))}, turning off AC")
        switch = switchBot()
        try:
            switch.connect()
            switch.set_ac("off")
            ac_state = "off"
        except HttpAccessTokenRefreshError:
            pass # Hope it works next time

def turn_off_AC():
    global ac_state
    if ac_state != "off":
        print(f"It's nearing wakeup time, turning off AC")
        switch = switchBot()
        try:
            switch.connect()
            switch.set_ac("off")
            ac_state = "off"
        except HttpAccessTokenRefreshError:
            pass # Hope it works next time

print(f"Beginning daemon loop cycle")
while True:
    # New day, check for new alarms
    current_day = datetime.date.today()
    if last_day != current_day:
        print(f"New day - {red(current_day.strftime('%b %d, %Y'))}")
        last_day = current_day
        alarm_hour, alarm_minute = set_todays_alarms()
    
    now = datetime.datetime.now(pytz.timezone('EST'))
    now += datetime.timedelta(hours=1) # Daylights savings time adjustment
    
    if now.hour > BLINDS_CLOSE_HOUR or now.hour < alarm_hour:
        check_AC()
    if now.hour > BLINDS_CLOSE_HOUR or now.hour < alarm_hour:
        if blind_state != "close":
            print(f"Blinds are open past {red(format(BLINDS_CLOSE_HOUR,'02d'))}:{red('00')}, closing...")
            close_blinds()
    elif (now.hour == alarm_hour and (now.minute+CHECK_INTERVAL/60) > alarm_minute) or\
        now.hour > alarm_hour:
        if blind_state != "open":
            print(f"Blinds are closed within {red('10')} minutes of {red(format(alarm_hour,'02d'))}:{red(format(alarm_minute,'02d'))}, opening...")
            turn_off_AC() # In case it's still running in the morning
            open_blinds()

    # Check the time to see if it's blind opening time within this cycle
    time.sleep(CHECK_INTERVAL)
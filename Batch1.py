import RPi.GPIO as GPIO
import time
from mfrc522 import SimpleMFRC522
import os
import requests
import pandas as pd
from twilio.rest import Client


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

# dataframe for storing uid values
rfid_data=pd.DataFrame(columns=['Vehicle Number','Offence'])

Trig = 40
Echo = 38
buzzer_pin = 29

GPIO.setmode(GPIO.BOARD)
GPIO.setup(Trig, GPIO.OUT)
GPIO.setup(Echo, GPIO.IN)
GPIO.setup(buzzer_pin, GPIO.OUT)

# Function to activate the buzzer
def activate_buzzer():
    GPIO.output(buzzer_pin, GPIO.HIGH)

# Function to deactivate the buzzer
def deactivate_buzzer():
    GPIO.output(buzzer_pin, GPIO.LOW)

try:
  while True:
     
        # RFID reading loop
        reader = SimpleMFRC522()
        id, text = reader.read()
        print(id, ":", text)

        # Get distance from sensor
        print("Initialising sensor")
        GPIO.output(Trig, False)
        time.sleep(2E-6)
        GPIO.output(Trig, True)
        time.sleep(10E-6)
        GPIO.output(Trig, False)
        while GPIO.input(Echo) == 0:
            pulse_start = time.time()
        while GPIO.input(Echo) == 1:
            pulse_end = time.time()
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)
        print("Distance : ",distance)
        violation=""
        #Violation : Pedestrian lane cutting
        if distance > 17 and distance < 24:
            print("Violation : Pedestrian lane cutting")
            violation="Pedestrian lane cutting"
            print("Vehicle number:",text)
            # Set environment variables for your credentials
            account_sid = "AC5b4ff006ca933bcd1bdfac9a7d31338b"
            auth_token = "7d95e1ed0ab0bdc5fd41290255fd098b"
            client = Client(account_sid, auth_token)
            message = client.messages.create(
              body="You have been fined Rs.500 for pedestrian lane cutting by vehicle number:{} ".format(text),
              from_="+14406353615",
              to="+919682643053")
           
            print(message.sid)
            # Activate the buzzer for 1 second
            activate_buzzer()
            time.sleep(2)
       
            # Deactivate the buzzer for 1 second
            deactivate_buzzer()
            time.sleep(10)

        # Violation : Red signal cutting and running
        elif distance < 17:
            print("Violation : Red signal cutting and running")
            violation="Red signal cutting and running"
            print("Vehicle number:",text)
            # Set environment variables for your credentials
            account_sid = "AC5b4ff006ca933bcd1bdfac9a7d31338b"
            auth_token = "7d95e1ed0ab0bdc5fd41290255fd098b"
            client = Client(account_sid, auth_token)
            message = client.messages.create(
              body="You have been fined Rs.2000 for red signal cutting and running",
              from_="+14406353615",
              to="+919682643053"
            )
            print(message.sid)
        elif distance > 24:
            violation = "none"
           
        x = {'Vehicle Number':text,'Offence':violation}
        rfid_data = pd.concat([rfid_data,pd.DataFrame(x, index=[-1])],ignore_index=True)
        rfid_data.to_csv('rfid_data.csv',index=False)
        csv_file=pd.read_csv("rfid_data.csv")
        html_output = csv_file.to_html(index=False)
        html_file = r"/home/aditikannan/Desktop/mini-project/rfid_data.html"
        with open(html_file,'w') as f:
            f.write(html_output)
            print("success")
           time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()

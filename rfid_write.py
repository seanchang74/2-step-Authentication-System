#!/usr/bin/env python
# -*- coding: utf8 -*-
import RPi.GPIO as GPIO
import mfrc522 as MFRC522
import signal

continue_reading = True
# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print("Ctrl+C captured, ending read.")
    continue_reading = False
    GPIO.cleanup()
# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)
# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()


# Welcome message
print("Welcome to the MFRC522 data write/read example")
print("Hold a tag near the reader")
print("Press Ctrl-C to stop.")


# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:
    # Scan for cards
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
    # If a card is found
    if status == MIFAREReader.MI_OK:
        print("Card detected")
    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()
    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:
        # Print UID
        print("Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3]))
        # This is the default key for authentication
        key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)
        # Authenticate
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)
        print("\n")
        # Check if authenticated
        if status == MIFAREReader.MI_OK:
            # Variable for the data to write
            my_name = "RaspberryPi 1234"
            data = []
            # Fill the data with my_name
            for x in range(0,len(my_name)):
                data.append(ord(my_name[x]))
            print("Sector 8 will now be filled with data in code:")
            # Write the data
            MIFAREReader.MFRC522_Write(8, data)
            print("\n")
            print("It now looks like this:")
            # Check to see if it was written
            rdData = MIFAREReader.MFRC522_Read(8)
            print ("No. 8")
            print ("Card read Data 0-3: "+str(rdData[0])+","+str(rdData[1])+","+str(rdData[2])+","+str(rdData[3]))
            print ("Card read Data 4-7: "+str(rdData[4])+","+str(rdData[5])+","+str(rdData[6])+","+str(rdData[7]))
            print ("Card read Data 8-11: "+str(rdData[8])+","+str(rdData[9])+","+str(rdData[10])+","+str(rdData[11]))
            print ("Card read Data 12-15: "+str(rdData[12])+","+str(rdData[13])+","+str(rdData[14])+","+str(rdData[15]))
            print("\n")
            # Stop
            MIFAREReader.MFRC522_StopCrypto1()
            # Make sure to stop reading for cards
            continue_reading = False
        else:
            print("Authentication error")

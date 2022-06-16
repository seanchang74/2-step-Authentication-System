import sys, smbus2, subprocess
from time import sleep
import mfrc522 as MFRC522
import RPi.GPIO as GPIO
from playsound import playsound
sys.modules['smbus'] = smbus2
from RPLCD.i2c import CharLCD

GPIO.setmode(GPIO.BCM)
lcd = CharLCD('PCF8574', address=0x27, port=1, backlight_enabled=True)

green_led = 17
GPIO.setup(green_led,GPIO.OUT)
red_led = 27
GPIO.setup(red_led,GPIO.OUT)
MIFAREReader = MFRC522.MFRC522()

def main():
    try:
        while True:
            # Scan for cards
            (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
            # If a card is found
            if status == MIFAREReader.MI_OK:
                print("Card detected")
                (status,uid) = MIFAREReader.MFRC522_Anticoll()
                if status == MIFAREReader.MI_OK:
                    id = ""
                    for num in uid:
                        id += str(num)
                    print("Card read UID: {0}".format(id))
                    # This is the default key for authentication
                    key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
                    # Select the scanned tag
                    MIFAREReader.MFRC522_SelectTag(uid)
                    # Authenticate
                    status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)
                    if status == MIFAREReader.MI_OK:
                        token_str = ""
                        token = MIFAREReader.MFRC522_Read(8)
                        for ascii in token:
                            token_str += chr(ascii)

                        if(token_str == "RaspberryPi 1234"):
                            #pass
                            lcd.clear()
                            lcd.cursor_pos = (0, 0)
                            lcd.write_string("Start FaceDetect")
                            lcd.cursor_pos = (1, 0)
                            lcd.write_string("Look Camera!")
                            sleep(3)
                            
                            r = subprocess.Popen(["python","face_detect.py"],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
                            out, err = r.communicate()
                            if(out.decode("utf-8").find("Authentication Pass") == -1):
                                #detect stranger
                                lcd.clear()
                                lcd.cursor_pos = (0, 0)
                                lcd.write_string("Face Auth Failed")
                                lcd.cursor_pos = (1, 0)
                                lcd.write_string("Detect Stranger!")
                                GPIO.output(green_led, 0)
                                GPIO.output(red_led, 1)
                                playsound("sound/alarm.mp3")
                            else:
                                lcd.clear()
                                lcd.cursor_pos = (0, 0)
                                #can be replaced by label name
                                lcd.write_string("Hello Sean")
                                lcd.cursor_pos = (1, 0)
                                lcd.write_string("Welcome Home!")
                                GPIO.output(red_led, 0)
                                GPIO.output(green_led, 1)
                                playsound("sound/correct.mp3")
                            sleep(3)
                            lcd.clear()
                        else:
                            # wrong password
                            lcd.clear()
                            lcd.cursor_pos = (0, 0)
                            lcd.write_string("Wrong Password")
                            lcd.cursor_pos = (1, 0)
                            lcd.write_string("Use Another Card")
                            GPIO.output(green_led, 0)
                            GPIO.output(red_led, 1)
                            playsound("sound/error.mp3")
                            sleep(3)
                            lcd.clear()

                        # Stop
                        MIFAREReader.MFRC522_StopCrypto1()
                        sleep(1)
                    else:
                        playsound("sound/error.mp3")
                        lcd.clear()
                        lcd.cursor_pos = (0, 0)
                        lcd.write_string("Just Try Again!")
                
    except:
        GPIO.cleanup()
        lcd.clear()
        raise

if __name__ == "__main__":
    main()

# Two-factor authentication system
An Authentication System using both RFID card and Face detection to verify your identity. System is implement on **Raspberry Pi 4**.

### Demo Video
Please Click [Here](https://www.youtube.com/watch?v=us4LwwhOKxs)

### Environment
- System Architecture
```shell=
admin@raspberrypi:~ $ uname -a
Linux raspberrypi 5.15.32-v8+ #1538 SMP PREEMPT Thu Mar 31 19:40:39 BST 2022 aarch64 GNU/Linux

admin@raspberrypi:~ $ cat /etc/os-release
PRETTY_NAME="Debian GNU/Linux 11 (bullseye)"
NAME="Debian GNU/Linux"
VERSION_ID="11"
VERSION="11 (bullseye)"
VERSION_CODENAME=bullseye
ID=debian
HOME_URL="https://www.debian.org/"
SUPPORT_URL="https://www.debian.org/support"
BUG_REPORT_URL="https://bugs.debian.org/"
```
- Installed Package
You can use `pip install -r requirements.txt` to build the same environment
```
mfrc522==0.0.7
numpy==1.22.4
opencv-python==4.5.5.64
Pillow==9.1.1
playsound==1.3.0
protobuf==3.20.1
requests==2.27.1
requests-oauthlib==1.3.1
RPi.GPIO==0.7.1
RPLCD==1.3.0
six==1.16.0
smbus2==0.4.2
spidev==3.5
tensorboard==2.9.0
tensorboard-data-server==0.6.1
tensorboard-plugin-wit==1.8.1
tensorflow @ file:///tensorflow-2.9.0-cp39-none-linux_aarch64.whl
tensorflow-estimator==2.9.0
tensorflow-io-gcs-filesystem==0.26.0
tflite-runtime==2.8.0
tflite-support==0.4.0
urllib3==1.26.9
```
### Technique
- Raspberry Pi + Webcam + RFID
- Tensorflow + OpenCV
- Teachable Machine (train face detection model)

### Instruction
1. Using RFID Card
    - If user pass the RFID verification, then go to step 2
    - If failed, then 
        - LCD display "Wrong Password" 
        - LED turn red and the speaker play error.mp3
2.	Start face detection 
    - If user pass, then
        - LCD display "Welcome Home"
        - LED turn green and the speaker play correct.mp3
    - If failed, then
        - LCD display "Detect Stranger!"
        - LED turn red and the speaker play error.mp3
        - Send the stranger photo to the house owner by email and line notify mechanism

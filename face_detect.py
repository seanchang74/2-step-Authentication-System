# Copyright 2018 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import smbus2, sys
import RPi.GPIO as GPIO
import numpy as np
from PIL import Image
import tensorflow as tf
import cv2, time, argparse, subprocess

sys.modules['smbus'] = smbus2
from RPLCD.i2c import CharLCD
GPIO.setmode(GPIO.BCM)
lcd = CharLCD('PCF8574', address=0x27, port=1, backlight_enabled=True)

img_folder = 'img'
def load_labels(filename):
  with open(filename, 'r') as f:
    return [line.strip() for line in f.readlines()]

def capture_img():
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if not ret:
        print("failed to grab frame")
        return img_folder + "/image_0.jpg"

    localtime = time.localtime()
    img_filename = str(localtime.tm_year) + "_" + str(localtime.tm_mon) + "_" + str(localtime.tm_mday) + \
                  "-" + str(localtime.tm_hour) + ":" + str(localtime.tm_min) + ":" + str(localtime.tm_sec)
    img_name = img_folder + "/{}.jpg".format(img_filename)
    cv2.imwrite(img_name, frame)
    print("{} written!".format(img_name))
    return img_name

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
      '-m',
      '--model_file',
      default='./model/model.tflite',
      help='.tflite model to be executed')
    parser.add_argument(
      '-l',
      '--label_file',
      default='./model/labels.txt',
      help='name of file containing labels')
    parser.add_argument(
      '--input_mean',
      default=127.5, type=float,
      help='input_mean')
    parser.add_argument(
      '--input_std',
      default=127.5, type=float,
      help='input standard deviation')
    parser.add_argument(
      '--num_threads', default=None, type=int, help='number of threads')
    parser.add_argument(
      '-e', '--ext_delegate', help='external_delegate_library path')
    parser.add_argument(
      '-o',
      '--ext_delegate_options',
      help='external delegate options, \
            format: "option1: value1; option2: value2"')

    args = parser.parse_args()
    # capture_img
    image = capture_img()
    lcd.clear()
    lcd.cursor_pos = (0, 0)
    lcd.write_string("Image Captured!")

    ext_delegate = None
    ext_delegate_options = {}

    # parse extenal delegate options
    if args.ext_delegate_options is not None:
        options = args.ext_delegate_options.split(';')
        for o in options:
            kv = o.split(':')
            if (len(kv) == 2):
                ext_delegate_options[kv[0].strip()] = kv[1].strip()
            else:
                raise RuntimeError('Error parsing delegate option: ' + o)

    # load external delegate
    if args.ext_delegate is not None:
        print('Loading external delegate from {} with args: {}'.format(
            args.ext_delegate, ext_delegate_options))
        ext_delegate = [
            tflite.load_delegate(args.ext_delegate, ext_delegate_options)
        ]

    interpreter = tf.lite.Interpreter(
      model_path=args.model_file,
      experimental_delegates=ext_delegate,
      num_threads=args.num_threads)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # check the type of the input tensor
    floating_model = input_details[0]['dtype'] == np.float32

    # NxHxWxC, H:1, W:2
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]
    img = Image.open(image).resize((width, height))

    # add N dim
    input_data = np.expand_dims(img, axis=0)

    if floating_model:
        input_data = (np.float32(input_data) - args.input_mean) / args.input_std

    interpreter.set_tensor(input_details[0]['index'], input_data)

    lcd.clear()
    lcd.cursor_pos = (0, 3)
    lcd.write_string("Scanning...")
    lcd.cursor_pos = (1, 3)
    lcd.write_string("Please Wait")

    start_time = time.time()
    interpreter.invoke()
    stop_time = time.time()

    output_data = interpreter.get_tensor(output_details[0]['index'])
    results = np.squeeze(output_data)

    top_k = results.argsort()[-5:][::-1]
    labels = load_labels(args.label_file)

    i = top_k[0]
    if floating_model:
        print('{:08.6f}: {}'.format(float(results[i]), labels[i]))
    else:
        print('{:08.6f}: {}'.format(float(results[i] / 255.0), labels[i]))

    pred = labels[i].replace('0','').strip()
    if (pred == "No Mask"):
        print("Authentication Pass")
    else:
        print("Stranger Detect!")
        time = image.replace('img/','').replace('.jpg','')
        cmd = "python send_mail.py --image {} --stamp {}".format(image,time)
        status = subprocess.call(cmd, shell=True)

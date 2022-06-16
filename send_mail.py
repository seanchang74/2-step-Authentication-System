import smtplib, argparse
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument(
  '-i',
  '--image',
  default='./img/image_0.jpg',
  help='pack image file')
parser.add_argument(
  '-s',
  '--stamp',
  default='',
  help='happen time')

args = parser.parse_args()

with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
    try:
        smtp.ehlo()  # 驗證SMTP伺服器
        smtp.starttls()  # 建立加密傳輸
        smtp.login("raspberrypi.face.detection@gmail.com", "pzpwkmekrtdfzgsh")  # 登入寄件者gmail

        content = MIMEMultipart()  # 建立MIMEMultipart物件
        content["subject"] = "樹莓派監控系統"  # 郵件標題
        content["from"] = "raspberrypi.face.detection@gmail.com"  # 寄件者
        content["to"] = "chungsean74@gmail.com"  # 收件者
        happen_time = args.stamp
        happen_time = happen_time.replace('_','/').replace('-','  ')
        content.attach(MIMEText("於{}時\n發現陌生人持有家中門禁卡，並試圖進入家中!".format(happen_time)))  # 郵件純文字內容
        content.attach(MIMEImage(Path(args.image).read_bytes()))  # 郵件圖片內容
        smtp.send_message(content)  # 寄送郵件
        print("Alert Email has already sent!")
    except Exception as e:
        print("Error message: ", e)
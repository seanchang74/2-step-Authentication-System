#基本功能測試
import requests, argparse

def lineNotifyMessage(imgpath):
    token = "Your Line Notify Token"
    msg = "發現陌生人持有家中門禁卡，並試圖進入家中!"
    headers = {
        "Authorization": "Bearer " + token
    }

    payload = {'message': msg}
    image = {'imageFile': open(str(imgpath), 'rb')}
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload, files = image)
    return r.status_code


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '-i',
      '--image',
      default='./img/image_0.jpg',
      help='pack image file')

  args = parser.parse_args()
  status_code = lineNotifyMessage(args.image)
  print(status_code)

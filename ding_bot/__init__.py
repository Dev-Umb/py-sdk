import http.client
import json

class DingBot:
    def __init__(self,token:str, prefix:str):
        self.token = token
        self.prefix = prefix
    def dingBotSendMsg(self, msg: str):
       conn = http.client.HTTPSConnection("oapi.dingtalk.com")
       body = {
          "msgtype": "text",
          "text": {
             "content": f'{self.prefix}{msg}'
          },
          "isAtAll": False
       }
       payload = json.dumps(body)
       headers = {
          'Content-Type': 'application/json',
          'Accept': '*/*',
          'Host': 'oapi.dingtalk.com',
          'Connection': 'keep-alive'
       }
       conn.request("POST", f"/robot/send?access_token={self.token}", payload, headers)
       res = conn.getresponse()
       data = res.read()
       print(data.decode("utf-8"))


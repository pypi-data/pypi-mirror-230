from connectsrhft import ConnectChannel
import json


class Test(ConnectChannel) :

    def __init__(self):
        data = {
                "apikey":"78fb717d49a88ff046708c8f922675f3a8043373a8cfab777faf233b0531e314",
                "secretkey":'0b3786c4671b3f7cdad873b28ee457c1',
                "baseURL":"http://52.66.127.232:8006/cosmicconnect" ,
                "wsURL":"ws://52.66.127.232:8006/api/cosmicconnect"   
            }
        super().__init__(data)

    def on_open(self, ws):
        print("connected!!")


    def on_close(self, ws, close_status_code, close_msg):
        print(close_msg)
    
    def on_message(self, ws, message):
        print(" MESSAGE RECIEVED : - ",message)
        message=json.loads(message)
        if message.get('status')=='success':
            ws.send(json.dumps({"event":"addTicker","token":47244684767}))

    def on_error(self, ws, error):
        print("============================================= || ERROR || ========================================== \n",error)

Test()
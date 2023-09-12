import pickle
from json import loads,dumps
from abc import ABC,abstractmethod
import websocket
import requests

class ConnectSRHFT_API :

    """
        Class : ConnectSRHFT 
        params to pass in constructor : 
            apikey : apikey provided for loggin in to rest api of rms
    
    """

    def __init__(self,kwargs) :
        self.dataSerializer(kwargs)            
        self._pickleFile = "session.pkl"
        # LOGGING IN TO API ENDPOINT
        self.__login()
        self.__urls = None
        self.accesstoken=None
        self.header = {}
        try :
            with open(self._pickleFile,"rb") as file :
                pkd = pickle.load(file) 
                self.__urls=pkd.urls   
                self.accesstoken=pkd.accesstoken   
        except Exception as e:
            print(e)

        # self.header['csrftoken'] = self.
        self.http = HTTPRequest(self.__baseURL+"/")

    def _getNetPositions(self):
        url_details=self.__urls.get('getNetPosition')
        print(url_details)
        response = self.http.post(url_details.get('endPoint'),json={"event":url_details.get("event"),"access_token":self.accesstoken, "data":{   }})
        return response.json()
    
    def _getTradebook(self):
        url_details=self.__urls.get('getTradeBook')
        print(url_details)
        response = self.http.post(url_details.get('endPoint'),json={"event":url_details.get("event"),"access_token":self.accesstoken, "data":{   }})
        return response.json()
    
    def _getOrderLogs(self):
        url_details=self.__urls.get('getOrderLogs')
        print(url_details)
        response = self.http.post(url_details.get('endPoint'),json={"event":url_details.get("event"),"access_token":self.accesstoken, "data":{   }})
        return response.json()
    
    def _getOrderErrorLogs(self):
        url_details=self.__urls.get('getOrderErrorLogs')
        print(url_details)
        response = self.http.post(url_details.get('endPoint'),json={"event":url_details.get("event"),"access_token":self.accesstoken, "data":{   }})
        return response.json()
    
    def _getContracts(self):
        url_details=self.__urls.get('getContracts')
        print(url_details)
        response = self.http.post(url_details.get('endPoint'),json={"event":url_details.get("event"),"access_token":self.accesstoken, "data":{   }})
        return response.json()
       

    def dataSerializer(self,__data):
        """
            CHECKING FOR KEYS IN DATA 
        """

        if isinstance(__data,dict):
            try:
                self.__apikey = __data["apikey"]
                self.__secretkey = __data["secretkey"]
                self.__baseURL = __data["baseURL"]
                self._wsURL = __data["wsURL"]
            except KeyError as e:
                raise KeyError(str(e)+ "is missing please check")                  
        else :
            raise TypeError("Object of unsupproted type cannot be serialized")

    def __login(self):
        try:
            __body = {
                "event":"login",
                "source":"web",
                "data":{
                    "apikey":self.__apikey,
                    "secretkey":self.__secretkey
                }
            }
            __response = requests.post(url=self.__baseURL+"/login",json=__body)
            if __response.status_code == 200 :
                # print(loads(__response.text).get('urls'))  
                # print(loads(__response.text).get('result').get('access_token'))

                __session = Session(sessionid=__response.cookies.get("sessionid"),csrf=__response.cookies.get("csrftoken"),accesstoken=loads(__response.text).get('result').get('access_token'),urls=loads(__response.text).get('urls'))
                with open(self._pickleFile,"wb") as f :
                    pickle.dump(__session,f)   
                print("logged in successfully")
            else :
                print(__response.text)
        except Exception as e:
            print(e)


class HTTPRequest:
    def __init__(self, base_url):
        self.base_url = base_url

    def get(self, endpoint, params=None, headers=None):
        url = self.base_url + endpoint
        response = requests.get(url, params=params, headers=headers)
        return response

    def post(self, endpoint, data=None, json=None, headers=None):
        url = self.base_url + endpoint
        response = requests.post(url, data=data, json=json, headers=headers)
        return response

    def put(self, endpoint, data=None, json=None, headers=None):
        url = self.base_url + endpoint
        response = requests.put(url, data=data, json=json, headers=headers)
        return response

    def delete(self, endpoint, headers=None):
        url = self.base_url + endpoint
        response = requests.delete(url, headers=headers)
        return response


class ConnectChannel(ConnectSRHFT_API,ABC) :

    def __init__(self,kwargs):
        super().__init__(kwargs)
        self.__sessionData = None
        
        try :
            with open(self._pickleFile,"rb") as file :
                self.__sessionData = pickle.load(file)    
        except Exception as e:
            print(e)
        print(self.__sessionData.accesstoken)
        self.websocket = None
        self.run()

    @abstractmethod
    def on_message(self, ws, message):
        pass

    @abstractmethod        
    def on_error(self, ws, error):
        pass

    @abstractmethod
    def on_close(self, ws, close_status_code, close_msg):
        pass

    @abstractmethod
    def on_open(self, ws):
        print("Opened connection")

    def run(self):
        websocket.enableTrace(True)
        # ws_headers = [("Cookie", f"csrftoken={self.__sessionData.csrf};sessionid={self.__sessionData.sessionid}")]
        # print(ws_headers)
        self.websocket = websocket.WebSocketApp(
            # self._wsURL+f"?access_token={self.__sessionData.accesstoken}",     
            self._wsURL,     
            cookie=f"access_token={self.__sessionData.accesstoken}",       
            # header=ws_headers,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )


        self.websocket.run_forever()  # 5 second reconnect delay if connection closed unexpectedly


class Session :
    """
        setter and getter class to store data in pickle file
    """

    def __init__(self,**kwargs) :
        self.__sessionid = kwargs.get("sessionid")
        self.__csrf = kwargs.get("csrf")
        self.__accesstoken = kwargs.get("accesstoken")
        self.__urls = kwargs.get("urls")

    @property
    def sessionid(self):
        return self.__sessionid     

    @sessionid.setter
    def sessionid(self,value):
        self.__sessionid = value

    @property
    def csrf(self):
        return self.__csrf     

    @csrf.setter
    def csrf(self,value):
        self.__csrf = value

    @property
    def accesstoken(self):
        return self.__accesstoken
    
    @accesstoken.setter
    def accesstoken(self,value):
        self.__accesstoken = value 

    @property
    def urls(self):
        return self.__urls
    
    @urls.setter
    def urls(self,value):
        self.__urls = value 

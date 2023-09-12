import pickle,os,requests
from json import loads
import sys,websocket,time,SharedArray
from datetime import datetime
import pandas as pd

class ConnectSRHFT :

    def __init__(self) :
        self.baseDir="/home/centos/WebTradingSystem/sharedMemory"
        self.packet={
            "tokenid2": 0,
            "bid0": 1,
            "bidqty0": 2,
            "ask0": 3,
            "askqty0": 4,
            "bid1": 5,
            "bidqty1": 6,
            "ask1": 7,
            "askqty1": 8,
            "bid2": 9,
            "bidqty2": 10,
            "ask2": 11,
            "askqty2": 12,
            "bid3": 13,
            "bidqty3": 14,
            "ask3": 15,
            "askqty3": 16,
            "bid4": 17,
            "bidqty4": 18,
            "ask4": 19,
            "askqty4": 20,
            "ltp": 21,
            "ltq": 22,
            "vtt": 23,
            "openinterest": 24,
            "netchangeindicator": 25,
            "averagetradeprice": 26,
            "lasttradetime": 27,
            "tradingstatus": 28,
            "openprice": 29,
            "closingprice": 30,
            "highprice": 31,
            "lowprice": 32
        }
        

    def dataSerializer(self,__data):
        """
            CHECKING FOR KEYS IN DATA 
        """
        
        if isinstance(__data,dict):
            print(__data)
            try:
                self.__apikey = __data["apikey"]
                self.__secretkey = __data["secretkey"]
                self.__loginURL = __data["loginURL"]
                self._wsURL = __data["wsURL"]
            except KeyError as e:
                raise KeyError(str(e)+ "is missing please check")                  
        else :
            raise TypeError("Object of unsupproted type cannot be serialized")

    def _login(self,creds=dict()):
        self._pickleFile = "session.pkl"
        self.__sessionData= None

        try :
            with open(self._pickleFile,"rb") as file :
                self.__sessionData = pickle.load(file)    
        except Exception as e:
            print("while reading pickle",e)
        
        self.dataSerializer(creds)            

        try:
            __body = {
                "event":"login",
                "source":"web",
                "data":{
                    "apikey":self.__apikey,
                    "secretkey":self.__secretkey
                }
            }
            __response = requests.post(url=self.__loginURL,json=__body)
            print(__response.text)
            if __response.status_code == 200 :                
                __session = Session(sessionid=__response.cookies.get("sessionid"),csrf=__response.cookies.get("csrftoken"),accesstoken=loads(__response.text).get("access_token"))
                with open(self._pickleFile,"wb") as f :
                    pickle.dump(__session,f)   
                print("logged in successfully")
            else :
                print("response from api ============== ",__response.text)
                sys.exit(1)
        except Exception as e:
            print("Error while connecting to api",e)

    def _connectWebSocket(self):
        try:
            self.websocket = websocket.create_connection(self._wsURL,cookie=f"csrftoken={self.__sessionData.csrf};sessionid={self.__sessionData.sessionid}")
        except Exception as e:
            print("Error on connectWebSocket ",e)
            print("Retry...")
            time.sleep(1)
            self._connectWebSocket()

    def _getMarketFeed(self,token=str()):
        message = {}        
        try :
            sa = SharedArray.attach(f"file://{self.baseDir}/tickers/{token}",ro=True)
            message = dict( (value,sa[i]) for i,value in enumerate(self.packet))
            return message
        except Exception as e :
            print("Error on getMarketFeed",e)
            return {}
        
    def _getNetPositions(self,clientid=str(),date=str(datetime.now().strftime('%Y%m%d'))):
        try :
            filename = f"{self.baseDir}/clients/{str(clientid)}/netposition/netposition{date}.csv" 
            res=pd.read_csv(filename).fillna(0)
            return res.to_dict('records')
        except Exception as e :
            print("Error on _getNetPositions",e)
            return []
        
    def _getTradebook(self,clientid=str(),date=str(datetime.now().strftime('%Y%m%d'))):
        try :
            filename = f"{self.baseDir}/clients/{str(clientid)}/tradebook/tradebook{date}.csv" 
            res=pd.read_csv(filename).fillna(0)
            return res.to_dict('records')
        except Exception as e :
            print("Error on _getTradebook",e)
            return []

class Session :
    """
        setter and getter class to store data in pickle file
    """

    def __init__(self,**kwargs) :
        self.__sessionid = kwargs.get("sessionid")
        self.__csrf = kwargs.get("csrf")
        self.__accesstoken = kwargs.get("accesstoken")

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
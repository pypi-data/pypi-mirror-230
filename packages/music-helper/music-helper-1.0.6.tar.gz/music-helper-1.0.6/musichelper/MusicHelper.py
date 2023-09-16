from .Deezer import Deezer
from .SoundCloud import Sound_Cloud
from .YTM import YTM

import concurrent.futures
import asyncio
import logging



class DummyClass:
    def __init__(self, _type:str="deezer") -> None:
        if _type == 'deezer': self.message = 'ARL is not provided'
        elif _type == 'soundcloud': self.message = 'Check the `sc_data` parameter when initializing MusicHelper'
        elif _type == 'ytm': self.message = 'Check the `ytm_oauth` parameter when initializing MusicHelper. If you do not have data for authorization, specify the path where to save them, and run'
    
    
    def __getattr__(self, name):
        def dummy_method(*args, **kwargs):
            raise ValueError(self.message)
        return dummy_method

class MusicHelper:
    def __init__(self, deezer_arl:str=None, ytm_oauth:str=None, sc_data:tuple=(None, None),
                logger:logging.Logger=None) -> None:
        
        self.executor = concurrent.futures.ThreadPoolExecutor()
        self.logger = logger 
        httpx_logger = logging.getLogger("httpx")
        httpx_logger.setLevel(logging.ERROR)

        self.deezer_status = False
        self.ytm_status = False
        self.sc_status = False


        
        if deezer_arl:
            self.deezer_status = True
            self.deezer = Deezer(arl = deezer_arl,logger = self.logger)
        else: self.deezer = DummyClass(_type = 'deezer')


        if ytm_oauth:
            self.ytm = YTM(ytm_oauth = ytm_oauth, logger = self.logger)
            self.ytm_status = True
        else: self.ytm = DummyClass(_type = 'ytm')


        if sc_data[0] is not None:
            self.sc_status = True
            self.sc_clientid, self.authtoken = sc_data
            self.soundcloud = Sound_Cloud(client_id = self.sc_clientid, 
                                         auth_token = self.authtoken,
                                         executor = self.executor,
                                         logger = self.logger)

        else: self.soundcloud = DummyClass(_type = 'soundcloud')

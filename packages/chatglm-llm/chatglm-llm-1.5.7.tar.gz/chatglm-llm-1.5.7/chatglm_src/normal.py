
import json
import time
import datetime
import re

import tqdm
import pandas as pd

from hashlib import md5
from typing import Iterable
from functools import reduce
from typing import Any
from typing import List

from websocket import create_connection
from termcolor import colored

class SmallModel:
    remote_host_ :str = None
    def __init__(self,name, remote=None):
        if remote is None:
            remote = self.__class__.remote_host_
        assert remote is not None
        self.remote_host  = remote
        self.name = name
        self._ok = False
        self.purpose = "unKnow"
    
    
    def status(self):
        try:
            ws = create_connection(f"ws://{self.remote_host}:15000")
            user_id = md5(time.asctime().encode()).hexdigest()
            TODAY = datetime.datetime.now()
            PASSWORD = "ADSFADSGADSHDAFHDSG@#%!@#T%DSAGADSHDFAGSY@#%@!#^%@#$Y^#$TYDGVDFSGDS!@$!@$" + f"{TODAY.year}-{TODAY.month}"
            ws.send(json.dumps({"user_id":user_id, "password":PASSWORD}))
            res = ws.recv()
            if res != "ok":
                print(colored("[info]:","yellow") ,res)
                raise Exception("password error")
            res = self.send_and_recv(json.dumps({"embed_documents":[self.name], "method":"status"}),ws)
            return res
        except Exception as e:
            raise e
        finally:
            ws.close()
    
    @classmethod
    def from_remote(cls, name,remote=None):
        if remote is None:
            remote = cls.remote_host_
        else:
            cls.remote_host_ = remote
        assert remote is not None
        model = cls(name, remote)
        model.try_load_in_remote()
        return model
    
    @classmethod
    def gpu_info_remote(cls, remote=None):
        if remote is None:
            remote = cls.remote_host_
        else:
            cls.remote_host_ = remote
        assert remote is not None
        ws = create_connection(f"ws://{remote}:15000")
        user_id = md5(time.asctime().encode()).hexdigest()
        TODAY = datetime.datetime.now()
        PASSWORD = "ADSFADSGADSHDAFHDSG@#%!@#T%DSAGADSHDFAGSY@#%@!#^%@#$Y^#$TYDGVDFSGDS!@$!@$" + f"{TODAY.year}-{TODAY.month}"
        ws.send(json.dumps({"user_id":user_id, "password":PASSWORD}))
        res = ws.recv()
        if res != "ok":
            print(colored("[info]:","yellow") ,res)
            raise Exception("password error")
        res = cls.send_and_recv(json.dumps({"embed_documents":["all"], "method":"gpu"}),ws)["embed"]
        ress = []
        for o in res:
            used, allcan = o.split("/",1)
            ress.append({"used":int(used.strip()[:-3]), "all":int(allcan.strip()[:-3]), "c":"MiB"})
        return ress
    
    @classmethod
    def clean_all(cls, remote=None):
        if remote is None:
            remote = cls.remote_host_
        else:
            cls.remote_host_ = remote
        assert remote is not None
        all_models = cls.show_all_loaded_models(remote)
        ws = create_connection(f"ws://{remote}:15000")
        user_id = md5(time.asctime().encode()).hexdigest()
        TODAY = datetime.datetime.now()
        PASSWORD = "ADSFADSGADSHDAFHDSG@#%!@#T%DSAGADSHDFAGSY@#%@!#^%@#$Y^#$TYDGVDFSGDS!@$!@$" + f"{TODAY.year}-{TODAY.month}"
        ws.send(json.dumps({"user_id":user_id, "password":PASSWORD}))
        res = ws.recv()
        if res != "ok":
            print(colored("[info]:","yellow") ,res)
            raise Exception("password error")
        res = cls.send_and_recv(json.dumps({"embed_documents":all_models, "method":"clean"}),ws)
        return res
    
    @classmethod
    def show_all_loaded_models(cls, remote=None):
        if remote is None:
            remote = cls.remote_host_
        else:
            cls.remote_host_ = remote
        assert remote is not None
        ws = create_connection(f"ws://{remote}:15000")
        user_id = md5(time.asctime().encode()).hexdigest()
        TODAY = datetime.datetime.now()
        PASSWORD = "ADSFADSGADSHDAFHDSG@#%!@#T%DSAGADSHDFAGSY@#%@!#^%@#$Y^#$TYDGVDFSGDS!@$!@$" + f"{TODAY.year}-{TODAY.month}"
        ws.send(json.dumps({"user_id":user_id, "password":PASSWORD}))
        res = ws.recv()
        if res != "ok":
            print(colored("[info]:","yellow") ,res)
            raise Exception("password error")
        res = cls.send_and_recv(json.dumps({"embed_documents":["all"], "method":"ls"}),ws)
        return res["embed"]

    @classmethod
    def show_all_models(cls, remote=None):
        if remote is None:
            remote = cls.remote_host_
        else:
            cls.remote_host_ = remote
        assert remote is not None
        ws = create_connection(f"ws://{remote}:15000")
        user_id = md5(time.asctime().encode()).hexdigest()
        TODAY = datetime.datetime.now()
        PASSWORD = "ADSFADSGADSHDAFHDSG@#%!@#T%DSAGADSHDFAGSY@#%@!#^%@#$Y^#$TYDGVDFSGDS!@$!@$" + f"{TODAY.year}-{TODAY.month}"
        ws.send(json.dumps({"user_id":user_id, "password":PASSWORD}))
        res = ws.recv()
        if res != "ok":
            print(colored("[info]:","yellow") ,res)
            raise Exception("password error")
        res = cls.send_and_recv(json.dumps({"embed_documents":["all"], "method":"ls-all"}),ws)
        return res["embed"]
        
    def clean(self):
        try:
            ws = create_connection(f"ws://{self.remote_host}:15000")
            user_id = md5(time.asctime().encode()).hexdigest()
            TODAY = datetime.datetime.now()
            PASSWORD = "ADSFADSGADSHDAFHDSG@#%!@#T%DSAGADSHDFAGSY@#%@!#^%@#$Y^#$TYDGVDFSGDS!@$!@$" + f"{TODAY.year}-{TODAY.month}"
            ws.send(json.dumps({"user_id":user_id, "password":PASSWORD}))
            res = ws.recv()
            if res != "ok":
                print(colored("[info]:","yellow") ,res)
                raise Exception("password error")
            res = self.send_and_recv(json.dumps({"embed_documents":[self.name], "method":"clean"}),ws)
            return res["embed"]
        except Exception as e:
            raise e
        finally:
            ws.close()

    
    def down_remote(self, try_time=3):
        try:
            ws = create_connection(f"ws://{self.remote_host}:15000")
            user_id = md5(time.asctime().encode()).hexdigest()
            TODAY = datetime.datetime.now()
            PASSWORD = "ADSFADSGADSHDAFHDSG@#%!@#T%DSAGADSHDFAGSY@#%@!#^%@#$Y^#$TYDGVDFSGDS!@$!@$" + f"{TODAY.year}-{TODAY.month}"
            ws.send(json.dumps({"user_id":user_id, "password":PASSWORD}))
            res = ws.recv()
            if res != "ok":
                print(colored("[info]:","yellow") ,res)
                raise Exception("password error")
            res = self.send_and_recv(json.dumps({"embed_documents":[self.name], "method":"clone"}),ws)
            time.sleep(2)
            res = self.msg()
            if "git clone failed: exit status 128" in res:
                print(colored("[Err : ]:","yellow") , colored(res,"red"))
                if try_time > 0:
                    return self.down_remote(try_time-1)
            return res["embed"]
            
        except Exception as e:
            raise e
        finally:
            ws.close()

    @classmethod
    def send_and_recv(cls, data, ws):
        try:
            T = len(data)// (1024*102)
            bart = tqdm.tqdm(total=T,desc=colored(" + sending data","cyan"))
            bart.leave = False
            for i in range(0, len(data), 1024*102):
                bart.update(1)
                ws.send(data[i:i+1024*102])
            bart.clear()
            bart.close()

            ws.send("[STOP]")
            message = ""
            total = int(ws.recv())
            bar = tqdm.tqdm(desc=colored(" + receiving data","cyan", attrs=["bold"]), total=total)
            bar.leave = False
            while 1:
                res = ws.recv()
                message += res
                bar.update(len(res))
                if message.endswith("[STOP]"):
                    message = message[:-6]
                    break
            bar.clear()
            bar.close()
            msg = json.loads(message)
            return msg
        except Exception as e:
            raise e
    
    def msg(self):
        try:
            ws = create_connection(f"ws://{self.remote_host}:15000")
            user_id = md5(time.asctime().encode()).hexdigest()
            TODAY = datetime.datetime.now()
            PASSWORD = "ADSFADSGADSHDAFHDSG@#%!@#T%DSAGADSHDFAGSY@#%@!#^%@#$Y^#$TYDGVDFSGDS!@$!@$" + f"{TODAY.year}-{TODAY.month}"
            ws.send(json.dumps({"user_id":user_id, "password":PASSWORD}))
            res = ws.recv()
            if res != "ok":
                print(colored("[info]:","yellow") ,res)
                raise Exception("password error")
            res = self.send_and_recv(json.dumps({"embed_documents":[self.name], "method":"msg"}),ws)
            return res.get("embed","")
        except Exception as e:
            raise e
        finally:
            ws.close()
    
    def change_remote_name(self, new_name):
        assert "/" not in new_name
        assert " " not in new_name
        ss = re.findall(r"[\w\-\_]+",new_name)
        assert len(ss) == 1 and ss[0] == new_name
        if self.name in self.show_all_models():
            try:
                ws = create_connection(f"ws://{self.remote_host}:15000")
                user_id = md5(time.asctime().encode()).hexdigest()
                TODAY = datetime.datetime.now()
                PASSWORD = "ADSFADSGADSHDAFHDSG@#%!@#T%DSAGADSHDFAGSY@#%@!#^%@#$Y^#$TYDGVDFSGDS!@$!@$" + f"{TODAY.year}-{TODAY.month}"
                ws.send(json.dumps({"user_id":user_id, "password":PASSWORD}))
                res = ws.recv()
                if res != "ok":
                    print(colored("[info]:","yellow") ,res)
                    raise Exception("password error")
                res = self.send_and_recv(json.dumps({"embed_documents":[self.name, new_name], "method":"change_name"}),ws)
                return res["embed"]
            except Exception as e:
                raise e
            finally:
                ws.close()
        else:
            raise Exception("model not exists")

    def check(self):
        self._ok = False
        name = self.name
        if "/" in name:
            name = name.rsplit("/",1)[-1]

        ws = create_connection(f"ws://{self.remote_host}:15000")
        user_id = md5(time.asctime().encode()).hexdigest()
        TODAY = datetime.datetime.now()
        PASSWORD = "ADSFADSGADSHDAFHDSG@#%!@#T%DSAGADSHDFAGSY@#%@!#^%@#$Y^#$TYDGVDFSGDS!@$!@$" + f"{TODAY.year}-{TODAY.month}"
        ws.send(json.dumps({"user_id":user_id, "password":PASSWORD}))
        res = ws.recv()
        if res != "ok":
            print(colored("[info]:","yellow") ,res)
            raise Exception("password error")
        reply =  self.send_and_recv(json.dumps({"embed_documents":[name], "method":"check"}), ws)["embed"]
        if reply.startswith("ok"):
            if ":" in reply:
                self.purpose = reply.split(":",1)[-1].strip()
            self._ok = True
        else:
            self.try_load_in_remote()

        return self._ok
    
    def try_load_in_remote(self):
        try:
            self._ok = False
            name = self.name
            if "/" in name:
                name = name.rsplit("/",1)[-1]
                
            ws = create_connection(f"ws://{self.remote_host}:15000")
            user_id = md5(time.asctime().encode()).hexdigest()
            TODAY = datetime.datetime.now()
            PASSWORD = "ADSFADSGADSHDAFHDSG@#%!@#T%DSAGADSHDFAGSY@#%@!#^%@#$Y^#$TYDGVDFSGDS!@$!@$" + f"{TODAY.year}-{TODAY.month}"
            ws.send(json.dumps({"user_id":user_id, "password":PASSWORD}))
            res = ws.recv()
            if res != "ok":
                print(colored("[info]:","yellow") ,res)
                raise Exception("password error")
            reply = self.send_and_recv(json.dumps({"embed_documents":[name], "method":"load"}), ws)["embed"]
            if reply.startswith("ok"):
                self._ok = True
                if ":" in reply:
                    self.purpose = reply.split(":",1)[-1].strip()
                return True
                
            return False
        except Exception as e:
            raise e
        finally:
            ws.close()

    # def show_remote_models(self):
    #     try:
    #         name = self.name
    #         if "/" in name:
    #             name = name.rsplit("/",1)[-1]
                
    #         ws = create_connection(f"ws://{self.remote_host}:15000")
    #         user_id = md5(time.asctime().encode()).hexdigest()
    #         TODAY = datetime.datetime.now()
    #         PASSWORD = "ADSFADSGADSHDAFHDSG@#%!@#T%DSAGADSHDFAGSY@#%@!#^%@#$Y^#$TYDGVDFSGDS!@$!@$" + f"{TODAY.year}-{TODAY.month}"
    #         ws.send(json.dumps({"user_id":user_id, "password":PASSWORD}))
    #         res = ws.recv()
    #         if res != "ok":
    #             print(colored("[info]:","yellow") ,res)
    #             raise Exception("password error")
    #         return self.send_and_recv(json.dumps({"embed_documents":[name], "method":"show"}), ws)["embed"]
    #     except Exception as e:
    #         raise e
    #     finally:
    #         ws.close()

    def __call__(self, args: List[str], pandas=True) -> Any:
        if isinstance(args, str):
            args = [args]
        assert isinstance(args, (list, tuple,Iterable,))
        if not self._ok:
            self.check()

        if not self._ok :
            raise Exception("remote's service no such model deployed"+self.name)
        ws = create_connection(f"ws://{self.remote_host}:15000")
        user_id = md5(time.asctime().encode()).hexdigest()
        TODAY = datetime.datetime.now()
        PASSWORD = "ADSFADSGADSHDAFHDSG@#%!@#T%DSAGADSHDFAGSY@#%@!#^%@#$Y^#$TYDGVDFSGDS!@$!@$" + f"{TODAY.year}-{TODAY.month}"
        ws.send(json.dumps({"user_id":user_id, "password":PASSWORD}))
        # time.sleep(0.5)
        res = ws.recv()
        if res != "ok":
            print(colored("[info]:","yellow") ,res)
            raise Exception("password error")
        name = self.name
        if "/" in name:
            name = name.rsplit("/",1)[-1]
            
        data = json.dumps({"embed_documents":args, "method": name})
        try:
            msg = self.send_and_recv(data, ws)
            o = self._merged(msg["embed"])
            if pandas:
                oss = []
                if len(o) > 0 and isinstance(o[0], str):
                    return o
                for i,ii in enumerate(o):
                    ar = args[i]
                    if isinstance(ii, dict ):
                        ii["input"] = ar
                    oss.append(ii)
                if isinstance(oss[0], dict):
                    return pd.DataFrame(oss)
                return oss
            return o
        except Exception as e:
            raise e
            # import ipdb;ipdb.set_trace()
    
    def _merged(self, res_list):
        res = []
        for one_obj in res_list:
            if isinstance(one_obj, list) :
                if len(one_obj) > 1:
                    if isinstance(one_obj[0], dict):
                        res.append({k:reduce(lambda x,y: x+y , map(lambda x: x[k] ,one_obj)) for k in one_obj[0]})
                    else:
                        res.append(one_obj)
                else:
                    res.append(one_obj[0])
            else:
                res.append(one_obj)
        return res
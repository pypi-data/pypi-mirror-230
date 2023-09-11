
import datetime
import time
import json
import inspect

from typing import Iterable, List
from aiowebsocket.converses import AioWebSocket
from websocket import create_connection
from hashlib import md5
from termcolor import colored

def is_async_method(method):
    return inspect.iscoroutinefunction(method)

class BaseLLM:
    remote_host :str = None
    callbacks : List = None

    def send_to_remote(self,data,ws):
        """
        every chunk of data is 2M
        """
        for i in range(0, len(data), 1024*1024*2):
            ws.send(data[i:i+1024*1024*2])
        ws.send("[STOP]")

    async def asend_to_remote(self, data, ws):
        """
        every chunk of data is 2M
        """
        for i in range(0, len(data), 1024*1024*2):
            await ws.send(data[i:i+1024*1024*2])
        await ws.send("[STOP]")

    def remote_call(self, prompt, stop):
        TODAY = datetime.datetime.now()
        PASSWORD = "ADSFADSGADSHDAFHDSG@#%!@#T%DSAGADSHDFAGSY@#%@!#^%@#$Y^#$TYDGVDFSGDS!@$!@$" + f"{TODAY.year}-{TODAY.month}"
        assert self.remote_host is not None
        
        ws = create_connection(f"ws://{self.remote_host}:15000")
        user_id = md5(time.asctime().encode()).hexdigest()
        # self.callback_manager =  langchain.callbacks.base.BaseCallbackManager(self.callbacks)
        
        # self.callback_manager =  BaseCallbackManager(self.callbacks)
        # self.callback_manager.set_handlers(self.callbacks)
        ws.send(json.dumps({"user_id":user_id, "password":PASSWORD}))
        # time.sleep(0.5)
        res = ws.recv()
        if res != "ok":
            print(colored("[info]:","yellow") ,res)
            raise Exception("password error")
        result = ''
        data = json.dumps({
            "model":"vicuna-13b",
            "prompt":prompt,
            "history":self.history,
            "temperature": self.temperature,
            })
        self.send_to_remote(data, ws)
        
        for callback in self.callbacks:
            if  is_async_method(callback.on_llm_start):continue
            callback.on_llm_start(
                None,
                prompt,
                run_id=user_id,
                verbose=self.verbose
            )
        while 1:
            res = ws.recv()
            msg = json.loads(res)
            # { "new":delta,"response": response, "history": history,"query": prompt}
            if "stop" in msg:
                break
            new_token = msg["new"]
            response = msg["response"]
            history = msg["history"]
            msg["verbose"] = self.verbose
            # self.remote_callback(new_token, history, response)
            
            # self.callback_manager.on_llm_new_token(new_token, **msg)
            for callback in self.callbacks:
                if  is_async_method(callback.on_llm_new_token):continue
                callback.on_llm_new_token(
                    new_token,
                    **msg
                )
            result = response
        for callback in self.callbacks:
            if  is_async_method(callback.on_llm_end):continue
            callback.on_llm_end(result, verbose=self.verbose)
        
        self.history = self.history+[[prompt, result]]
        return result

    async def async_remote_call(self, prompt):
        uri = f"ws://{self.remote_host}:15000"
        result = ''
        TODAY = datetime.datetime.now()
        PASSWORD = "ADSFADSGADSHDAFHDSG@#%!@#T%DSAGADSHDFAGSY@#%@!#^%@#$Y^#$TYDGVDFSGDS!@$!@$" + f"{TODAY.year}-{TODAY.month}"
        # self.callback_manager =  BaseCallbackManager(self.callbacks)
        # self.callback_manager.set_handlers(self.callbacks)
        async with AioWebSocket(uri) as aws:
            converse = aws.manipulator
            
            user_id = md5(time.asctime().encode()).hexdigest()
            await converse.send(json.dumps({"user_id":user_id, "password":PASSWORD}).encode())
            res = await converse.receive()
            res = res.decode()
            if res != "ok":
                raise Exception("password error:"+res)
            data = json.dumps({"prompt":prompt, "history":self.history,"model":"chatglm","temperature":self.temperature}).encode()
            await self.asend_to_remote(data, converse)

            for call in self.callbacks:
                if is_async_method(call.on_llm_start):
                    await call.on_llm_start(prompt, None, verbose=self.verbose)
            while 1:
                res = await converse.receive()
                msg = json.loads(res.decode())
                # { "new":delta,"response": response, "history": history,"query": prompt}
                if "stop" in msg:
                    break
                new_token = msg["new"]
                response = msg["response"]
                msg["verbose"] = self.verbose
                for call in self.callbacks:
                    if is_async_method(call.on_llm_start):
                        await call.on_llm_new_token(new_token, **msg)
                result = response
        self.history = self.history+[[prompt, result]]
        for call in self.callbacks:
            if is_async_method(call.on_llm_start):
                await call.on_llm_end(result, verbose=self.verbose)
        return result
    

    def stream(self,prompt: str, stop: List[str] = None):
        TODAY = datetime.datetime.now()
        PASSWORD = "ADSFADSGADSHDAFHDSG@#%!@#T%DSAGADSHDFAGSY@#%@!#^%@#$Y^#$TYDGVDFSGDS!@$!@$" + f"{TODAY.year}-{TODAY.month}"
        assert self.remote_host is not None
        uri = f"ws://{self.remote_host}:15000"
        result = ''
        # self.callback_manager =  BaseCallbackManager(self.callbacks)
        # self.callback_manager.set_handlers(self.callbacks)
        
        ws = create_connection(f"ws://{self.remote_host}:15000")
        user_id = md5(time.asctime().encode()).hexdigest()
        # self.callback_manager =  langchain.callbacks.base.BaseCallbackManager(self.callbacks)
        
        # self.callback_manager =  BaseCallbackManager(self.callbacks)
        # self.callback_manager.set_handlers(self.callbacks)
        ws.send(json.dumps({"user_id":user_id, "password":PASSWORD}))
        # time.sleep(0.5)
        res = ws.recv()
        if res != "ok":
            print(colored("[info]:","yellow") ,res)
            raise Exception("password error")
        result = ''
            
            
        data = json.dumps({"prompt":prompt, "history":self.history,"model":"chatglm", "temperature": self.temperature})
        self.send_to_remote(data, ws)
        while 1:
            res = ws.recv()
            msg = json.loads(res)
            # { "new":delta,"response": response, "history": history,"query": prompt}
            if "stop" in msg:
                break
            new_token = msg["new"]
            response = msg["response"]
            history = msg["history"]
            msg["verbose"] = self.verbose
            result = msg
            yield msg
            
            # for call in self.callbacks:
            #     if is_async_method(call.on_llm_start):
                    # await call.on_llm_end(result, verbose=self.verbose)
        self.history = self.history+[[prompt, result]]
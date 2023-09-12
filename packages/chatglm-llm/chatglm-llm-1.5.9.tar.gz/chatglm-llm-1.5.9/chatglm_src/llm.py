from asyncio import coroutines
from typing import List, Optional
import langchain
import sys
# from langchain.callbacks.manager import Callbacks
from langchain.llms.base import LLM
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import requests
import json
from typing import Iterable, List
import pathlib
import os, json
import asyncio
from termcolor import colored
import tempfile
import datetime
import inspect
from hashlib import md5
import time
import tqdm
import numpy as np
from aiowebsocket.converses import AioWebSocket
from websocket import create_connection
import websockets
from websockets.server import serve
from langchain.embeddings import HuggingFaceEmbeddings
import gptcache
from gptcache.processor.pre import get_prompt
from gptcache.manager.factory import get_data_manager
from .cluster_and_smi import cluster, similarity
from .hf import HF
from .git import Git
from .base import BaseLLM
try:
    from langchain.cache import GPTCache
except:
    pass

from concurrent.futures import ThreadPoolExecutor,as_completed

try:
    
    from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification
    from fastchat.serve.inference import load_model
    from fastchat.conversation import get_default_conv_template
    from accelerate import load_checkpoint_and_dispatch
    
    from fastchat.serve.inference import generate_stream
    import torch, gc
    DEFAULT_CACHE_MAP_PATH = str(pathlib.Path.home() / ".cache" / "local_qa_cache_map")
    i = 0

    def init_gptcache_map(cache_obj: gptcache.Cache):
        global i
        cache_path = f'{DEFAULT_CACHE_MAP_PATH}_{i}.txt'
        cache_obj.init(
            pre_embedding_func=get_prompt,
            data_manager=get_data_manager(data_path=cache_path),
        )
        i += 1
    
    langchain.llm_cache = GPTCache(init_gptcache_map)
    # print(colored("init gptcache", "green"))
except Exception as e:
    print("use remote ignore this / load transformers failed, please install transformers and accelerate first and torch.")
from .callbacks import AsyncWebsocketHandler, AsyncWebSocksetCallbackManager

TEXT_EMB_PATH = pathlib.Path("~").expanduser() / ".cache"/"torch"/"sentence_transformers"/"GanymedeNil_text2vec-large-chinese"
TEXT_EMB_PATH = pathlib.Path("~").expanduser() / ".cache"/ "bge-large-zh"
TEXT_EMB_EN_PATH = pathlib.Path("~").expanduser() / ".cache"/ "bge-large-en"
if TEXT_EMB_PATH.exists():
    TEXT_EMB_PATH = str(TEXT_EMB_PATH)
else:
    TEXT_EMB_PATH = "GanymedeNil/text2vec-large-chinese"

def is_async_method(method):
    return inspect.iscoroutinefunction(method)
## LLM for chatglm
# only load from local's path
# default path is in ~/.cache/chatglm, if not exists, will download from huggingface'url :https://huggingface.co/THUDM/chatglm-6b
# 
"""Common utility functions for working with LLM APIs."""
import re
from typing import List, Dict, Any, Optional, Union

# from transformers import AutoModel, AutoTokenizer

os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"
def load_model_on_gpus(checkpoint_path, num_gpus=2):
    # 总共占用13GB显存,28层transformer每层0.39GB左右
    # 第一层 word_embeddings和最后一层 lm_head 层各占用1.2GB左右
    num_trans_layers = 28
    vram_per_layer = 0.39
    average = 13/num_gpus
    used = 1.2
    device_map = {'transformer.word_embeddings': 0,
                  'transformer.final_layernorm': num_gpus-1, 'lm_head': num_gpus-1}
    gpu_target = 0
    for i in range(num_trans_layers):
        if used > average-vram_per_layer/2 and gpu_target < num_gpus:
            gpu_target += 1
            used = 0
        else:
            used += vram_per_layer
        device_map['transformer.layers.%d' % i] = gpu_target

    model = AutoModel.from_pretrained(
        checkpoint_path, trust_remote_code=True)
    model = model.eval()
    model = load_checkpoint_and_dispatch(
        model, checkpoint_path, device_map=device_map, offload_folder="offload", offload_state_dict=True).half()
    return model

def auto_configure_device_map(num_gpus: int) -> Dict[str, int]:
    # transformer.word_embeddings 占用1层
    # transformer.final_layernorm 和 lm_head 占用1层
    # transformer.layers 占用 28 层
    # 总共30层分配到num_gpus张卡上
    num_trans_layers = 28
    per_gpu_layers = 30 / num_gpus

    # bugfix: 在linux中调用torch.embedding传入的weight,input不在同一device上,导致RuntimeError
    # windows下 model.device 会被设置成 transformer.word_embeddings.device
    # linux下 model.device 会被设置成 lm_head.device
    # 在调用chat或者stream_chat时,input_ids会被放到model.device上
    # 如果transformer.word_embeddings.device和model.device不同,则会导致RuntimeError
    # 因此这里将transformer.word_embeddings,transformer.final_layernorm,lm_head都放到第一张卡上
    device_map = {'transformer.word_embeddings': 0,
                  'transformer.final_layernorm': 0, 'lm_head': 0}

    used = 2
    gpu_target = 0
    for i in range(num_trans_layers):
        if used >= per_gpu_layers:
            gpu_target += 1
            used = 0
        assert gpu_target < num_gpus
        device_map[f'transformer.layers.{i}'] = gpu_target
        used += 1

    return device_map


def load_model_on_gpus_old(checkpoint_path, num_gpus: int = 2,device_map = None, **kwargs):
    if num_gpus < 2 and device_map is None:
        model = AutoModel.from_pretrained(checkpoint_path, trust_remote_code=True, **kwargs).half().cuda()
    else:
        from accelerate import dispatch_model
        model = AutoModel.from_pretrained(checkpoint_path, trust_remote_code=True, **kwargs).half()
        if device_map is None:
            device_map = auto_configure_device_map(num_gpus)
        model = dispatch_model(model, device_map=device_map)

    return model

def enforce_stop_tokens(text: str, stop: List[str]) -> str:
    """Cut off the text as soon as any stop words occur."""
    return re.split("|".join(stop), text)[0]

def auto_gc():
    if torch.cuda.is_available():
        # for all cuda device:
        for i in range(0,torch.cuda.device_count()):
            CUDA_DEVICE = f"cuda:{i}"
            with torch.cuda.device(CUDA_DEVICE):
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
    else:
        gc.collect()


class Vicuna13B(LLM):
    max_token: int = 2048
    temperature: float = 0.2
    top_p = 0.9
    top_k = 2
    history = []
    history_id = "default"
    tokenizer: Any = None
    model: Any = None
    history_len: int = 10
    model: Any = None
    tokenizer: Any = None
    model_path: str = pathlib.Path.home() / ".cache" / "vicuna-13b-f"
    cpu: bool = False
    streaming: bool = False
    verbose: bool = False
    callbacks :Any  = [StreamingStdOutCallbackHandler()]
    remote_host: Any = None
    @classmethod
    def load(cls, *args, model_path:str=None, **kwargs):
        mo = cls(*args, **kwargs)
        if mo.remote_host is not None:
            return mo
        if model_path is None:
            model_path = cls.model_path
        print(colored("[GPU]","green"),":",torch.cuda.device_count(), "GPUs" )
        mo.model, mo.tokenizer = load_model(model_path, device="cuda", num_gpus="auto")
        return mo   
    
    
    def set_history(self, hist:List[str]):
        self.history = hist
    
    
    @property
    def _llm_type(self) -> str:
        return "Vicuna-13b"
    
    
    def stream_output(self, prompt, on_llm_start,on_llm_new_token,on_llm_end):
        st = time.time()
        
        params = {
            "prompt": prompt,
            "temperature": self.temperature,
            "max_new_tokens": self.max_token,
            "top_p":0.9,
            # "top_k":k,
            # "beams_num":4,
            "stop": None,
        }

        # Stream output
        if "</s>" in prompt:
            history, input_prompt = prompt.split("</s>",1)
            history += " "
        else:
            history = ""
            input_prompt = prompt
        on_llm_start(prompt, None, verbose=self.verbose)
        all_text = ""
        delta = ""

        # print("AT:",prompt.encode())
        for i,response in enumerate(generate_stream(self.model, self.tokenizer, params, device="cuda",stream_interval=4)):
            all_text = response.encode()[len((history+input_prompt).encode()):]
            delta = all_text[len(delta):].decode("utf-8","ignore")
            data = {"response": response, "history": history,"query": prompt}
            if self.verbose:
                print(delta, end='', flush=True)
            self.callback_manager.on_llm_new_token(
                delta, verbose=self.verbose, **data
            )
        auto_gc()
        self.history = self.history+[[input_prompt.split("USER:",1)[1], all_text.decode("utf-8","ignore")]]
        pure_output = all_text.decode("utf-8","ignore")
        print("usage : ", time.time() - st, "s")
        return pure_output
    


    async def _acall(self, prompt: str, stop: List[str] = None):
        assert self.remote_host is not None
        uri = f"ws://{self.remote_host}:15000"
        TODAY = datetime.datetime.now()
        PASSWORD = "ADSFADSGADSHDAFHDSG@#%!@#T%DSAGADSHDFAGSY@#%@!#^%@#$Y^#$TYDGVDFSGDS!@$!@$" + f"{TODAY.year}-{TODAY.month}"
        async with AioWebSocket(uri) as aws:
            converse = aws.manipulator
            
            user_id = md5(time.asctime().encode()).hexdigest()
            await converse.send(json.dumps({"user_id":user_id, "password":PASSWORD}).encode())
            res = await converse.receive()
            res = res.decode()
            if res != "ok":
                raise Exception("password error:"+res)
            result = ''
            data = json.dumps({
                "model":"vicuna-13b",
                "prompt":prompt,
                "history":self.history,
                "temperature": self.temperature,
                }).encode()
            await self.asend_to_remote(data, converse)

            for callback in self.callbacks:
                if is_async_method(callback.on_llm_start):
                    await callback.on_llm_start(
                        None,
                        prompt,
                        run_id=user_id,
                        verbose=self.verbose
                    )
            while 1:
                res = await converse.receive()
                msg = json.loads(res.decode())
                # { "new":delta,"response": response, "history": history,"query": prompt}
                if "stop" in msg:
                    break
                new_token = msg["new"]
                response = msg["response"]
                history = msg["history"]
                msg["verbose"] = True
                for callback in self.callbacks:
                    if is_async_method(callback.on_llm_new_token):
                        await callback.on_llm_new_token(new_token, **msg)
                result = response
            self.history = self.history+[[prompt, result]]
            for callback in self.callbacks:
                if is_async_method(callback.on_llm_new_token):
                        await callback.on_llm_end(result, verbose=self.verbose)
            self.history = self.history+[[prompt, result]]
            return result

    def _call(self, prompt: str, stop: List[str]  = None, run_manager:Any = None) -> str:
        TODAY = datetime.datetime.now()
        PASSWORD = "ADSFADSGADSHDAFHDSG@#%!@#T%DSAGADSHDFAGSY@#%@!#^%@#$Y^#$TYDGVDFSGDS!@$!@$" + f"{TODAY.year}-{TODAY.month}"
        if self.remote_host is not None:
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
        else:
            current_completion = self.stream_output(prompt, run_manager.on_llm_start, run_manager.on_llm_new_token, run_manager.on_llm_end)
            return current_completion
    
    async def _ncall(self, aio,prompt,history, temperature=None):
        if history is not None and isinstance(history, list):
            self.history = history

        if "USER:" not in prompt and "ASSISTANT:" not in prompt:
            conv = get_default_conv_template("vicuna").copy()
            for p,o in self.history:
                conv.append_message(conv.roles[0], p+"\n")
                conv.append_message(conv.roles[1], o+"\n")
            conv.append_message(conv.roles[0], prompt+"\n")
            conv.append_message(conv.roles[1], None)
            prompt = conv.get_prompt()
        print(colored("prompt:", "green"),prompt, colored(" temperature:", "green"), temperature)
        
        params = {
            "prompt": prompt,
            "temperature": self.temperature,
            "max_new_tokens": self.max_token,
            "top_p":0.9,
            # "top_k":k,
            # "beams_num":4,
            "stop": None,
        }
        if temperature is not None:
            params["temperature"] = temperature

        # Stream output
        if "</s>" in prompt:
            history, input_prompt = prompt.split("</s>",1)
            history += " "
        else:
            history = ""
            input_prompt = prompt
        
        all_text = ""
        delta = ""

        # print("AT:",prompt.encode())
        old = ""
        sended = ""
        for i,response in enumerate(generate_stream(self.model, self.tokenizer, params, device="cuda")):
            all_text = response[len((history+input_prompt)):]
            
            try:
                if "�" in all_text:
                    continue
                delta = all_text[len(old):]
                old = all_text
                
                data = { "new":delta,"response": all_text, "history": history,"query": prompt}
                # print(colored("[delta]:","green"), delta)
                # print(colored("[currt]:","yellow"), all_text,end="\n\t---- io ----\n")
                await aio.send(json.dumps(data))
            except :
                continue
        data = { "new":delta,"response": all_text, "history": history,"query": prompt, "stop":True}
        # await aio.send(json.dumps(data))
        auto_gc()
        return data

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

class Qwen(LLM, BaseLLM):
    max_token: int = 8096
    temperature: float = 0.01
    top_p = 0.9
    history = []
    history_id = "default"
    tokenizer: Any = None
    model: Any = None
    history_len: int = 10
    model: Any = None
    tokenizer: Any = None
    model_path: str = pathlib.Path.home() / ".cache" / "Qwen-7B-Chat"
    cpu: bool = False
    streaming: bool = False
    verbose: bool = False
    callbacks :Any  = [StreamingStdOutCallbackHandler(), AsyncWebsocketHandler()]
    # callback_manager:  Any = BaseCallbackManager
    remote_host: Any = None

    @property
    def _llm_type(self) -> str:
        return "qwen-7b"
    
    def _call(self, prompt: str,stop, callbacks: any = None) -> str:
        """Generate text from the prompt."""
        TODAY = datetime.datetime.now()
        
        if self.remote_host is None:
            current_completion = ""
            if self.verbose:
                print("streaming")
            
            for response in self.model.chat_stream(self.tokenizer, prompt, self.history, max_length=self.max_token, top_p=self.top_p,
                                               temperature=self.temperature):
                delta = response[len(current_completion) :]
                current_completion = response
                data = {"response": response, "history": self.history,"query": prompt}
                if self.verbose:
                    print(delta, end='', flush=True)
                self.callback_manager.on_llm_new_token(
                    delta, verbose=self.verbose, **data
                )
            auto_gc()
            self.history = self.history+[[prompt, current_completion]]
            return current_completion
        else:
            if callbacks is not None:
                self.callbacks = callbacks
            return self.remote_call(prompt, stop)
    
    async def _acall(self, prompt:str, stop,callbacks=None) -> str:
        if callbacks is not None:
            self.callbacks = callbacks
        return await self.async_remote_call(prompt, stop)






class QwenVLLM:
    
    
    stop="<|im_end|>"
    start="<|im_start|>"
    def __init__(self, remote_host:str=None,port=15000, max_tokens:int=8096, temperature:float=0.0, top_p:float=1, system="You are a helpful assistant."):
        self.remote_host = remote_host
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.system=system
        self.api =f"http://{remote_host}:{port}/generate"
        self.history = []
    
    
    def make_context(self, query, history=[]):
        def _one_turn(role,content):
            return f"\n{self.start}{role}\n{content}{self.stop}"
        context = _one_turn("system", self.system).strip()
        if history is not None and isinstance(history , (list,tuple,)) and len(history) > 0:
            for q,h in history:
                context += _one_turn("user", q)
                context += _one_turn("assistant", h)
        context += _one_turn("user", query)
        return context + _one_turn("user", query) + f"\n{self.start}assistant\n"
    
    def parse_reply(self, reply, start="<|im_start|>"):
        """'<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n你好你能幹些什麼呢<|im_end|>\n<|im_start|>user\n你好你能幹些什麼呢<|im_end|>\n{start}assistant\n您好，我是一個大型語言模型，可以回答問題、提供建議、生成代码、聊天等。如果您有
    任何問題，請隨時向我提出，我會盡力回答。"""
        if f"\n{start}assistant\n" in reply:
            return reply.rsplit(f"\n{start}assistant\n")[1]
        return reply

    def _req(self,prompt: str, stream: bool = False) -> requests.Response:
        headers = {"User-Agent": "Test Client"}
        pload = {
            "prompt": prompt,
            "n": 1,
            "top_p": self.top_p,
            "use_beam_search": False,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stop": ["<|im_end|>","<|im_start|>"],
            "stream": stream,
        }
        response = requests.post(self.api, headers=headers, json=pload, stream=True)
        return response
    
    def get_streaming_response(response: requests.Response) -> Iterable[List[str]]:
        for chunk in response.iter_lines(chunk_size=8192,
                                        decode_unicode=False,
                                        delimiter=b"\0"):
            if chunk:
                data = json.loads(chunk.decode("utf-8"))
                output = data["text"]
                yield output


    def get_response(response: requests.Response) -> List[str]:
        data = json.loads(response.content)
        output = data["text"]
        return output

    def streaming(self, prompt):
        result = ""
        context_prompt = self.make_context(prompt, self.history)
        for output in self.get_streaming_response(self._req(context_prompt, stream=True)):
            result += output
            n = output[len(output):]
            msg = {"new":n,"response": output, "history": self.history,"query": prompt}
            yield msg
        self.history = self.history+[[prompt, result]]

    def stream_stdout(self, prompt):
        print(">>"+prompt)
        ws = ""
        st = time.time()
        for msg in self.streaming(prompt):
            n = msg["new"]
            ws += n
            sys.stdout.write(n)
            sys.stdout.flush()
        print(f"Tokens: {len(ws)} Speed {len(ws)/(time.time() -st)} tokens/s")

class ChatGLMLLM(LLM):
    """
            Load a model from local or remote
        if want to use stream mode:
            'streaming=True'
        if want to use langchain's Callback:
            examples: 'callbacks=[StreamingStdOutCallbackHandler(), AsyncWebsocketHandler()]'

        if want use cpu: # default will try to use gpu
            'cpu=True'
        
        if want to use remote's model:
            'remote_host="xx.xxx.xx.xx"'  , if set this , will auto call by ws://xx.xxx.xxx.xx:15000"
            optional:
                remote_callback: a callback function, will call when receive a new token like  'callback(new_token, history, response)'
                if not set, will print to stdout

    """
    max_token: int = 10000
    temperature: float = 0.01
    top_p = 0.9
    history = []
    history_id = "default"
    tokenizer: Any = None
    model: Any = None
    history_len: int = 10
    model: Any = None
    tokenizer: Any = None
    model_path: str = pathlib.Path.home() / ".cache" / "chatglm"
    cpu: bool = False
    streaming: bool = False
    verbose: bool = False
    callbacks :Any  = [StreamingStdOutCallbackHandler(), AsyncWebsocketHandler()]
    # callback_manager:  Any = BaseCallbackManager
    remote_host: Any = None


    @classmethod
    def load(cls, *args, model_path: str = None, **kargs):
        """
        Load a model from local or remote
        if want to use stream mode:
            'streaming=True'
        if want to use langchain's Callback:
            examples: 'callbacks=[StreamingStdOutCallbackHandler(), AsyncWebsocketHandler()]'

        if want use cpu: # default will try to use gpu
            'cpu=True'
        
        if want to use remote's model:
            'remote_host="xx.xxx.xx.xx"'  , if set this , will auto call by ws://xx.xxx.xxx.xx:15000"
            optional:
                remote_callback: a callback function, will call when receive a new token like  'callback(new_token, history, response)'
                if not set, will print to stdout


        """
        mo = cls(*args, **kargs)
        if "cpu" in kargs and kargs["cpu"]:
            mo.cpu = True
        if model_path is not None:
            mo.model_path = pathlib.Path(model_path)
        # load from local
        if mo.model_path.exists() and mo.remote_host is None:
            if torch.cuda.device_count() > 0:
                print(colored("[GPU]","green"),":",torch.cuda.device_count(), "GPUs" )
                # use chatglm
                try:
                    mo.model = load_model_on_gpus_old(mo.model_path, num_gpus=torch.cuda.device_count())
                except Exception as e:
                    print(colored("[GPU]","yellow"),": failed !! but try load use new way " + str(e),torch.cuda.device_count(), "GPUs" )
                    try:
                        from .chatglm_utils import load_model_on_gpus
                        mo.model = load_model_on_gpus(mo.model_path, num_gpus=torch.cuda.device_count())
                    except Exception as e:
                        print(colored("[GPU]","red"),": failed !! " + str(e),torch.cuda.device_count(), "GPUs" )

            else:
                mo.model = AutoModel.from_pretrained(mo.model_path, trust_remote_code=True, device_map="auto")
            mo.tokenizer = AutoTokenizer.from_pretrained(mo.model_path, trust_remote_code=True)
        else:
            # load from huggingface
            # use os.system to call git lfs download model
            # then load from local
            # TODO: use git lfs to download model
            pass
        if mo.remote_host is not None:
            return mo
        if mo.cpu:
            mo.model = mo.model.float()
        # else:
        #     mo.model = mo.model.half().cuda()
        mo.model = mo.model.eval()
        return mo
    
    def set_history(self, hist:List[str]):
        self.history = hist
    
    
    @property
    def _llm_type(self) -> str:
        return "ChatGLM"

    async def _acall(self, prompt: str, stop: List[str] = None):
        if self.streaming:
            # print("async ing ", self.callbacks)
            if not "(history_id:" in prompt:
                prompt = f"(history_id:{self.history_id})" + prompt

            if not isinstance(self.callback_manager, AsyncWebSocksetCallbackManager):
                self.callback_manager = AsyncWebSocksetCallbackManager([i for i in self.callbacks if isinstance(i, AsyncWebsocketHandler)])
            current_completion = ""
            # if self.callback_manager.is_async:
            prompt,history_id, history = await self.callback_manager.on_llm_start(
                prompt,
                None,
                verbose=self.verbose
            )
            if history_id is not None and history is not None:
                self.history_id = history_id
                self.history = history
            for response, history in self.model.stream_chat(self.tokenizer, prompt, self.history, max_length=self.max_token, top_p=self.top_p,
                                               temperature=self.temperature):
                
                delta = response[len(current_completion) :]
                current_completion = response
                data = {"response": response, "history": history,"query": prompt, "verbose":self.verbose}
                if self.callback_manager.is_async:
                    # print(".", end="", flush=True)
                    await self.callback_manager.on_llm_new_token(
                        delta, verbose=self.verbose, **data
                    )
                else:
                    # print("+", end="", flush=True)
                    self.callback_manager.on_llm_new_token(
                        delta, verbose=self.verbose, **data
                    )
            auto_gc()
            self.history = self.history+[[prompt, current_completion]]
            await self.callback_manager.on_llm_end(
                {
                    "id": self.history_id,
                    "history": self.history,
                },
                verbose=self.verbose
            )
            return current_completion
        elif self.remote_host is not None :
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


                
        else:
            response, _ = self.model.chat(
                self.tokenizer,
                prompt,
                history=self.history[-self.history_len:] if self.history_len > 0 else None,
                max_length=self.max_token,
                top_p=self.top_p,
                temperature=self.temperature,
            )
            response = enforce_stop_tokens(response, stop or [])
            self.history = self.history+[[prompt, response]]
            return response
    
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
        # yield result

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
    
    def _call(self, prompt: str, stop: List[str]  = None,run_manager: Any = None) -> str:
        TODAY = datetime.datetime.now()
        PASSWORD = "ADSFADSGADSHDAFHDSG@#%!@#T%DSAGADSHDFAGSY@#%@!#^%@#$Y^#$TYDGVDFSGDS!@$!@$" + f"{TODAY.year}-{TODAY.month}"
        if self.streaming:
            current_completion = ""
            if self.verbose:
                print("streaming")
            
            for response, history in self.model.stream_chat(self.tokenizer, prompt, self.history, max_length=self.max_token, top_p=self.top_p,
                                               temperature=self.temperature):
                delta = response[len(current_completion) :]
                current_completion = response
                data = {"response": response, "history": history,"query": prompt}
                if self.verbose:
                    print(delta, end='', flush=True)
                self.callback_manager.on_llm_new_token(
                    delta, verbose=self.verbose, **data
                )
            auto_gc()
            self.history = self.history+[[prompt, current_completion]]
            return current_completion
        elif self.remote_host is not None :
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
            
            for callback in self.callbacks:
                if is_async_method(callback.on_llm_start):continue
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
                    if is_async_method(callback.on_llm_start):continue
                    callback.on_llm_new_token(
                        new_token,
                        **msg
                    )
                result = response
            for callback in self.callbacks:
                if is_async_method(callback.on_llm_start):continue
                callback.on_llm_end(result, verbose=self.verbose)
            
            self.history = self.history+[[prompt, result]]
            return result
        else:
            response, _ = self.model.chat(
                self.tokenizer,
                prompt,
                history=self.history[-self.history_len:] if self.history_len>0 else [],
                max_length=self.max_token,
                temperature=self.temperature,
            )
            auto_gc()
            if stop is not None:
                response = enforce_stop_tokens(response, stop)
            self.history = self.history+[[prompt, response]]
            return response



class WebsocketWrap:
    def __init__(self, llm,embeding, websocket, mos={}):
        self.websocket = websocket
        self.llm = llm
        self.embeding = embeding
        self.exe = ThreadPoolExecutor(max_workers=5)
        self.mos = mos
        self.status = ""
        self.msg = ""
    
    async def reply(self, data):
        await self.websocket.send(str(len(data)))
        for i in range(0,len(data), 1024*1024*2):
            await self.websocket.send(data[i:i+1024*1024*2])
        await self.websocket.send("[STOP]")
    

    def clean(self, models):
        for m in models:
            if m in self.mos:
                print("clean:", m)
                Mo = self.mos[m]
                Mo.clean()
                del self.mos[m]
    
    def gpu_mem(self):
        return [i.split("|")[2].strip() for i in os.popen("nvidia-smi ").read().split("\n") if "Default " in i]
        
    
    async def __call__(self, 
                       prompt=None,model=None,temperature=None,
                       embed_documents=None,embed_query=None,
                       method=None, eps=None, min_samples=None,n_clusters=None,
                       filter_noise=None,
                       history=None):
        try:
            # assert prompt is not None 
            if prompt is not None:
                assert isinstance(prompt, str)
                assert model is not None
                if model == "chatglm":
                    llm = self.llm
                    current_completion = ""
                    if history is not None and isinstance(history, list):
                        llm.history = history
                    if temperature is not None:
                        llm.temperature = temperature
                    for response, history in llm.model.stream_chat(llm.tokenizer, prompt, llm.history, max_length=llm.max_token, top_p=llm.top_p,
                                                        temperature=llm.temperature):
                        delta = response[len(current_completion) :]
                        current_completion = response
                        data = { "new":delta,"response": response, "history": history,"query": prompt}
                        await self.websocket.send(json.dumps(data))
                    data = { "new":delta,"response": response, "history": history,"query": prompt, "stop":True}
                elif model == "vicuna-13b":
                    
                    data = await self.llm._ncall(self.websocket, prompt, history,temperature=temperature)
                elif model == "config":
                    if prompt.startswith("start:"):
                        model = prompt.split(":",1)[1].strip()
                        self.exe.submit(self.load_model, model)
                    data = { "new":"X","response": "loading:"+model, "history": history,"query": prompt, "stop":True}
                
                else:

                    data = { "new":"X","response": "Not Support Model !:"+model, "history": history,"query": prompt, "stop":True}
                await self.websocket.send(json.dumps(data))
            elif embed_query is not None:
                res = self.embeding.embed_query(embed_query)
                data = { "embed":res} 
                data = json.dumps(data, cls=NumpyEncoder)
                await self.reply(data)
            elif embed_documents is not None and method is None:
                res = self.embeding.embed_documents(embed_documents)
                if filter_noise is not None:
                    # filter noise value in vec, for example: 
                    # vec exists 512 dim, but most of them are a small value, we can filter them
                    w = np.array(res)
                    w[np.abs(w) < filter_noise] = 0
                    res = w.tolist()
                data = { "embed":res}
                data = json.dumps(data, cls=NumpyEncoder)
                await self.reply(data)
            
            elif method is not None and embed_documents is not None:
                
                if method in ['kmeans', 'dbscan']:
                    res = self.embeding.embed_documents(embed_documents)
                    if filter_noise is not None:
                        # filter noise value in vec, for example: 
                        # vec exists 512 dim, but most of them are a small value, we can filter them
                        w = np.array(res)
                        w[np.abs(w) < filter_noise] = 0
                        res = w.tolist()

                    print(colored("[method]","green"),":",method, colored("[eps]","green"),":",eps, colored("[min_samples]","green"),":",min_samples, colored("[n_clusters]","green"),":",n_clusters)
                    labels = cluster(res, eps=eps, min_samples=min_samples, method=method, n_clusters=n_clusters)
                    data = {}
                    for ix, document in enumerate(embed_documents):
                        l = labels[ix]
                        if l < 0: # remove noise
                            continue
                        
                        data[l] = data.get(l, []) + [document]
                    data = json.dumps(data, cls=NumpyEncoder)
                    await self.reply(data)
                elif method in ["euclidean","cosine"]:
                    res = self.embeding.embed_documents(embed_documents)
                    if filter_noise is not None:
                        # filter noise value in vec, for example: 
                        # vec exists 512 dim, but most of them are a small value, we can filter them
                        w = np.array(res)
                        w[np.abs(w) < filter_noise] = 0
                        res = w.tolist()

                    data = {"similarity":similarity(res, method=method)}
                    data = json.dumps(data, cls=NumpyEncoder)
                    await self.reply(data)
                elif method == "check":
                    if len(embed_documents) == 0:
                        await self.reply(json.dumps({"embed":"no such !"}))
                        return
                    name = embed_documents[0]
                    if name in self.mos:
                        await self.reply(json.dumps({"embed":"ok:"+self.mos[name].purpose}))
                    await self.reply(json.dumps({"embed":"no such !"}))
                    return
                elif method == "change_name":
                    if len(embed_documents) != 2:
                        await self.reply(json.dumps({"embed":"err for name and new_name"}))
                        return
                    name, new_name = embed_documents
                    pp_old = pathlib.Path("~/.cache/").expanduser() / name
                    pp_new = pathlib.Path("~/.cache/").expanduser() / new_name
                    if pp_old.exists() and pp_old.is_dir():
                        if pp_new.exists():
                            await self.reply(json.dumps({"embed":"name exists !"}))
                            return
                        pp_old.rename(str(pp_new))
                        await self.reply(json.dumps({"embed":"ok"}))
                        return
                    await self.reply(json.dumps({"embed":"old not exists! : "+ str(pp_old)}))
                    return
                
                elif method == "show" or method == "ls":
                    
                    await self.reply(json.dumps({"embed":list(self.mos.keys())}))
                    return
                elif method == "ls-all" or method == "lsall":
                    ms = []
                    e = pathlib.Path("~/.cache/").expanduser()
                    for n in  os.listdir(e):
                        if n.endswith("/"):
                            n = n[:-1]
                        repo =  e / n / "config.json"
                        if repo.exists():
                            ms.append(n)

                    await self.reply(json.dumps({"embed": ms}))
                    return
                elif method == "load":
                    if len(embed_documents) == 0:
                        await self.reply(json.dumps({"embed":"no such !"}))
                        return
                    name = embed_documents[0]
                    if name in self.mos:
                        await self.reply(json.dumps({"embed":"ok:"+self.mos[name].purpose}))
                        return
                    msg = HF.load_model(name)
                    if isinstance(msg, str):
                        await self.reply(json.dumps({"embed":msg}))
                        return
                    Mo = msg[name]
                    if Mo.purpose == "embed":
                        self.embeding = Mo.model
                    self.mos[name] = msg[name]
                    await self.reply(json.dumps({"embed":"ok:"+ msg[name].purpose}))
                    return
                elif method == "clone" or method == "download":
                    if self.msg.startswith("downloading"):
                        await self.reply(json.dumps({"embed":self.msg + " [wait]"}))
                        return
                    print(colored("[download]","green"),":",embed_documents)
                    Git(embed_documents).start()
                    f = pathlib.Path(tempfile.tempdir) / "down.log"
                    if f.exists():
                        with open(f) as fp:
                            await self.reply(json.dumps({"embed":fp.read()}))
                    return
                
                elif method == "msg" or method == "status":
                    f = pathlib.Path(tempfile.tempdir) / "down.log"
                    if f.exists():
                        with open(f) as fp:
                            await self.reply(json.dumps({"embed":fp.read()}))
                    return
                elif method == "info" or method == "gpu":
                    await self.reply(json.dumps({"embed":self.gpu_mem()}))
                    return
                elif method == "clear" or method == "clean" or method =="remove" or method == "del":
                    self.clean(embed_documents)
                    await self.reply(json.dumps({"embed": self.gpu_mem()}))
                    return
                else:
                    e = self.mos.get(method, None)
                    if e != None and isinstance(embed_documents, (list, tuple,)):

                        res = e(embed_documents)
                        out = json.dumps({"embed":res}, cls=NumpyEncoder)
                        print(colored("[R]:","green"),":", len(out))
                        await self.reply(out)
                        return
                    
                    await self.reply(json.dumps({"msg":"not support method:"+method}))
        finally:
            auto_gc()



class AsyncServer:
    __users = {}
    _callbacks = {"hello": lambda x: colored("[hello]","green") + time.asctime()}
    llm = None
    embeding = None
    mos = {}

    @classmethod
    def load_model(cls, name):
        HF.load_model(name)
        cls.mos.update(HF.mos)


    @classmethod
    async def echo(cls,websocket):
        try:
            print(colored("[connected]","green"),":",websocket)
            no = 0
            messages = ""
            async for message in websocket:
                
                if no == 0:
                    if await cls.user(message, websocket):
                        no += 1
                        continue
                    else:
                        await websocket.close()
                        break
                if message.endswith("[STOP]"):
                    messages += message[:-6]
                    break
                else:
                    messages += message
                no += 1
            # if len(messages) < 1000:
            #     print(colored("[recv]","green") ,":",messages)
            # else:
            #     print(colored("[recv]","green") ,":",messages[:10]+ f"...{len(messages)}...{messages[-10:]}")
            m = messages[:100] + "..." + str(len(messages)) if len(messages) > 100 else messages
            print(colored("[recv]","green") ,":", m)
            if len(messages) == 0:
                await cls.del_user(websocket)
                return
            oneChat = WebsocketWrap(cls.llm,cls.embeding, websocket, mos=cls.mos)
            await oneChat(**json.loads(messages))
                


        except websockets.exceptions.ConnectionClosedOK:
            print(colored("[closed]","yellow"),":",websocket)
            await cls.del_user(websocket)
        except websockets.exceptions.ConnectionClosedError:
            print(colored("[closed]","red"),":",websocket)
            await cls.del_user(websocket)

        except Exception as e:
            
            print(colored("[error]","red"),":",e)
            raise e
    
    @classmethod
    def add_callback(cls, name, callback):
        cls._callbacks[name] = callback

    @classmethod
    async def call(cls, message, websocket):
        try:
            msgs = json.loads(message)
            if "user_id" not in msgs :
                await websocket.send("error")
                await websocket.close()
                await cls.del_user(websocket)
                return
            user_id = msgs["user_id"]
            if user_id not in cls.__users.values():
                await websocket.send("not login")
                await websocket.close()
                await cls.del_user(websocket)
                return
            if "callback" in msgs:
                callback = cls._callbacks[msgs["callback"]]
                args = msgs.get("args",[])
                kwargs = msgs.get("kwargs",{})

                res = await callback(*args, **kwargs)
                await websocket.send(json.dumps({
                    "result":res,
                    "user_id":user_id,
                    "callback":msgs["callback"],
                }))
            
        except Exception as e:
            print(colored("[error]","red"),":",e)
            await websocket.close()
            await cls.del_user(websocket)

    @classmethod
    async def main(cls, port):
        async with serve(cls.echo, "0.0.0.0", port):
            await asyncio.Future()  # run forever
    
    @classmethod
    async def user(cls, first_msg, websocket) -> bool:
        TODAY = datetime.datetime.now()
        PASSWORD = "ADSFADSGADSHDAFHDSG@#%!@#T%DSAGADSHDFAGSY@#%@!#^%@#$Y^#$TYDGVDFSGDS!@$!@$" + f"{TODAY.year}-{TODAY.month}"
        try:
            d = json.loads(first_msg)
            user_id = d["user_id"]
            password = d["password"]
            if password != PASSWORD:
                print("RIGHT: password is ", PASSWORD)
                return False
            print(colored("[user-login]","green"),":",user_id)
            cls.__users[websocket] =  user_id
            await websocket.send("ok")
            return True
        except Exception as e:
            print(colored("[error]","red"),":",websocket, e)
    
    @classmethod
    async def del_user(cls,websocket):
        if websocket in cls.__users:
            del cls.__users[websocket]

    @classmethod
    def start(cls,port=15000, model_path=None, name="chatglm"):
        cpu = False
        if not torch.cuda.is_available():
            cpu = True
        print(colored(f"[cpu:{cpu} ]","green"),":",f"listen:0.0.0.0:{port}")
        
        cls.embeding = HuggingFaceEmbeddings(model_name=TEXT_EMB_PATH)
        print(colored(f"[embedding: use cpu{cpu} ]","green"),":",f"{TEXT_EMB_PATH}")
        if name == "chatglm":
            cls.llm = ChatGLMLLM.load(model_path=model_path, cpu=cpu, streaming=True)
            print(colored(f"[ starting chatglm]","green"),":",f"listen:0.0.0.0:{port}")
        elif name == "vicuna-13b":
            cls.llm = Vicuna13B.load(model_path=model_path, cpu=cpu, streaming=True)
            print(colored(f"[ starting vicuna-13b]","green"),":",f"listen:0.0.0.0:{port}")
        asyncio.run(cls.main(port))



class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)
    
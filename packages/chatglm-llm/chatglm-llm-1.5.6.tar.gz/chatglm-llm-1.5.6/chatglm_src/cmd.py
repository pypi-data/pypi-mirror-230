from .llm import AsyncServer
import argparse
import pathlib

parser = argparse.ArgumentParser(description='Start a chatglm server.')
parser.add_argument('--port', type=int, default=15000, help='port number')
parser.add_argument("-p","--model-path", default=str(pathlib.Path.home() / ".cache" / "chatglm"), help="path to model directory")
parser.add_argument("-n","--name", default="chatglm", help="llm's name")
parser.add_argument("-e","--extend", nargs="*", help="load extend models , like 'emotion' 'ner' in ~/.cache/ ")


def main():
    args = parser.parse_args()
    if args.extend:
        for i in args.extend:
            AsyncServer.load_model(i)
    AsyncServer.start(port=args.port, model_path=args.model_path, name=args.name)
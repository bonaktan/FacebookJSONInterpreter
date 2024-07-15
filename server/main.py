#             buddha please make this work
#                        _oo0oo_
#                       o8888888o
#                       88" . "88
#                       (| -_- |)
#                       0\  =  /0
#                     ___/`---'\___
#                   .' \\|     |// '.
#                  / \\|||  :  |||// \
#                 / _||||| -:- |||||- \
#                |   | \\\  -  /// |   |
#                | \_|  ''\---/''  |_/ |
#                \  .-\__  '-'  ___/-. /
#              ___'. .'  /--.--\  `. .'___
#           ."" '<  `.___\_<|>_/___.' >' "".
#          | | :  `- \`.;`\ _ /`;.`/ - ` : | |
#          \  \ `_.   \_ __\ /__ _/   .-` /  /
#      =====`-.____`.___ \_____/___.-`___.-'=====
#                        `=---='

from bottle import Bottle, static_file, abort, request
from bottle_websocket import GeventWebSocketServer, websocket

# Webserver Side
app = Bottle()

@app.route('/')
def home():
    return static_file('index.html', root='./build/')

@app.get('/websocket', apply=[websocket])
def WebsocketInterface(ws):
    wsock = request.environ.get('wsgi.websocket')
    if not wsock:
        print('405')
        abort(405, "Don't access /websocket using a browser, it's a WebSocket")
    while True:
        try:
            message = wsock.receive()
            if message == None: continue
            print(message)
            wsock.send("Your message was: %r" % message)
        except WebSocketError:
            break

@app.route('/static/<filename:path>')
def statics(filename): return static_file(filename, root='./build/static')

# Main Engine, Entry = FacebookData(Path(path_to_rootfolder))
import os
import re
import json
import logging
import datetime
import jsonpickle

# from glob import glob
from pathlib import Path

from functools import partial


class Template:
    class Folders:
        def __init__(self, logIdentity, *args, **kwargs):
            # path definitions
            self.path = self.Parent.rootPath / self.identity
            if not self.path.is_dir():
                raise NotADirectoryError(
                    self.path, "Path given either does not exist or is a file."
                )
            self._setupLogHandlers(logIdentity)

        def _setupLogHandlers(self, name):
            self.logger = logging.getLogger(name)
            self.Parent.logstreamer.setFormatter(self.Parent.logformatter)

            self.logger.setLevel(self.Parent.options["log"])
            self.Parent.logstreamer.setLevel(self.Parent.options["log"])

        def __repr__(self):
            return f"FacebookData(/{self.identity})"

    class Conversation(Folders):
        def __init__(self, path, name, parent):
            self.Parent = parent
            self._setupLogHandlers("FacebookData.Activity.Messages.%s" % name)
            self.path = path
            self.internalName = name
            self.audios = self.__getFiles(self.path / "audio")
            self.files = self.__getFiles(self.path / "files")
            self.gifs = self.__getFiles(self.path / "gifs")
            self.photos = self.__getFiles(self.path / "photos")
            self.videos = self.__getFiles(self.path / "videos")
            self.jsonRaw = self.interpretJSONs(
                tuple(
                    self.path.glob("message_*.json"),
                )
            )
            
            # flags
            self.participants = []
            for _ in self.jsonRaw["participants"]:
                self.participants.append(_["name"])
            self.isGroupChat = True if len(self.participants) >= 3 else False
            self.name = (
                self.jsonRaw["title"]
                if self.jsonRaw["title"] != ""
                else self.internalName
            )
            self.messages = self.jsonRaw["messages"]
            self.convoLinks = self.__extractURL()
            self.logger.debug("Conversation with %s initialized", name)

        def interpretJSONs(self, jsonpath):
            with jsonpath[0].open(mode="rb") as jsondata:
                data = json.loads(jsondata.read(), cls=Template.FacebookJSONDecoder)
            if len(jsonpath) >= 2:
                for i in jsonpath[1:]:
                    with i.open(mode="rb") as jsondata:
                        adddata = json.loads(
                            jsondata.read(), cls=Template.FacebookJSONDecoder
                        )
                        data["messages"] += adddata["messages"]
            return data

        def __getFiles(self, path):
            return list(path.glob("*")) if path.is_dir() else None

        def __extractURL(self):
            result = []
            convoLinkRegex = r"(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])"
            convoLinkFilter = [
                "meet.google.com",
                "zoom.us",
                "us05web.zoom.us",
                "us04web.zoom.us",
            ]  # this links are used for online class, as such, does not serve any useful purpose
            for i in self.messages:
                if "content" not in i:
                    continue
                URL = re.findall(convoLinkRegex, i["content"])
                if URL == []:
                    continue
                for x in URL:
                    if x[1] in convoLinkFilter:
                        continue
                    result.append(f"{x[0]}://{x[1]}{x[2]}")
            return result

        def __repr__(self):
            return f"Conversation({self.name})"

    class FacebookJSONDecoder(json.JSONDecoder):
        def __init__(self, *args, **kwargs):
            json.JSONDecoder.__init__(
                self, object_hook=self.object_hook, *args, **kwargs
            )

        def object_hook(self, obj):
            for key, value in obj.items():
                if isinstance(value, str):  # fix the mojibake
                    obj[key] = value.encode("latin1").decode("utf-8")
                elif key == "timestamp_ms":
                    obj[key] = datetime.datetime.fromtimestamp(value / 1000)
            return obj


class FacebookData(Template.Folders):
    identity = ""  # should be / but weird stuffs happens in Template.Folders.__init__.pathdefinitions

    def __init__(self, root, *args, **kwargs):
        self.Parent = self
        self.rootPath = root
        # argument parsings
        self.options = {
            "log": logging.INFO,
        }
        self.options.update(kwargs)
        self._setup_logger()
        super().__init__("FacebookData", *args, **kwargs)
        self.logger.addHandler(self.Parent.logstreamer)
        self.logger.debug("Logging Initialized")

        self.Activity = FacebookActivity(self)
        self.logger.debug("FacebookData initialized")

    def _setup_logger(self):
        self.logstreamer = logging.StreamHandler()
        self.logformatter = logging.Formatter("%(levelname)s: %(name)s - %(message)s")


class FacebookActivity(Template.Folders):
    identity = "your_facebook_activity"

    def __init__(self, parent):
        self.Parent = parent
        # breakpoint()
        super().__init__("FacebookData.Activity")

        self.messages = Messages(parent)
        self.logger.debug("Activity initialized from %s", self.path)


class Messages(Template.Folders):
    identity = "your_facebook_activity/messages"

    def __init__(self, parent):
        self.Parent = parent
        super().__init__("FacebookData.Activity.Messages")
        # 2 types, archived, inbox
        self.archived = self.__parseMessageDirectory(
            "archived_threads"
        ) + self.__parseMessageDirectory("message_requests")
        self.inbox = self.__parseMessageDirectory(
            "e2ee_cutover"
        ) + self.__parseMessageDirectory("inbox")
        self.logger.debug("MessageRoot initialized from %s", self.path)

    def __parseMessageDirectory(self, subdir):
        result = []
        for i in (self.path / subdir).iterdir():
            name = "_".join(i.name.split("_")[:-1])
            if name == "":
                name = i.name
            result.append(Template.Conversation(i, name, self.Parent))
        return result


class FacebookExceptions:
    class InvalidDirectoryError(OSError):
        def __init__(self, directory, message=""):
            self.directory = directory
            self.message = (
                "Path given seems to be invalid, modified, or the wrong path"
                if message == ""
                else message
            )

        def __str__(self):
            return f"{self.message} ({self.directory})"

    
    
if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer
    from geventwebsocket import WebSocketError
    from geventwebsocket.handler import WebSocketHandler
    server = WSGIServer(('127.0.0.1', 42069), app,
                    handler_class=WebSocketHandler)
    print("Access at http://%s:%s/websocket.html" % ('127.0.0.1', 42069))
    server.serve_forever()
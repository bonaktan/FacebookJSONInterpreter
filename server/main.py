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

# this is all 1 file instead of a whole directory since i plan to literally merge EVERYTHING after compilation for release :3

from bottle import Bottle, static_file, request, run, response
import json
import re
import logging
import datetime
from pathlib import Path
# Webserver Side

app = Bottle()
Data = None


def returnData(returnType, **retData):
    retData["returnType"] = returnType  # NOTE: shall be validated
    return json.dumps(retData)

def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        response.headers["Access-Control-Allow-Origin"] = (
            "*"  # WARNING: can be a security risk, please merge server and client asap
        )
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = (
            "Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token"
        )
        if request.method != "OPTIONS":
            return fn(*args, **kwargs)
    return _enable_cors


@app.route("/")
def home():
    return static_file("index.html", root="./build/")


@app.route("/static/<filename:path>")
def statics(filename):
    return static_file(filename, root="./build/static")


@app.route("/api", method="POST")
@enable_cors
def api():
    # maybe compensate for the cors * with an ip check????
    clientRequest = json.loads(request.body.read())
    if clientRequest == {}:
        return returnData("communicationCheck", status=True)
    match clientRequest["requestType"]:
        case "setFilePath":
            global Data
            if Data:
                return returnData(returnType="error", code=-401)
            clientRequest["path"] = Path(clientRequest["path"])
            if not clientRequest["path"].exists():
                return returnData(returnType="error", code=-201)
            Data = FacebookData(
                clientRequest["path"]
            )  # we now have an entry point, now make it efficient
            return returnData("setFilePath", code=0)


# Engine Version 1.1.0
# Additions: Multiprocessing Support

from dataclasses import dataclass  # noqa: E402
from functools import partial  # noqa: E402


class ItemTemplates:
    @dataclass
    class Data:
        path: Path
        # the rest tba

    @dataclass
    class Media:
        path: Path
        mediaType: str

    class Conversation:
        path: Path
        name: str
        isGroupChat: bool
        isLoaded: bool
        Message: "ItemTemplates.ConvoMessage"

        def __init__(self, path):  # this shit slow as fuck
            self.path = path
            convoData = list(self.path.glob("message_*.json"))
            with convoData[0].open(mode="rb") as f:
                test = self.removeMessageJSON(f.read()) # f can reach up to 2mb on size
                messageData = json.loads(
                    test, cls=Structures.JSONDecoder
                )
            self.name = (
                messageData["title"] if messageData["title"] != "" else self.path.name
            )
            self.isGroupChat = True if len(messageData["participants"]) > 2 else False

        @staticmethod
        def removeMessageJSON(jsonData):
            # this will assume that the json is well formed
            # this will also assume that messages is entry2 of the json
            # it will tokenize shits
            tokens = []
            stack = []  # List[(flag, pos)]
            depth = 1
            pos = -1
            isQuotes = False
            escape = False
            for char in jsonData:  # pass1: parse only until a certain depth
                pos += 1
                if escape:
                    escape = False
                    continue
                match char:
                    case 92:  # \
                        escape = True
                        continue
                    case 34:  # "
                        isQuotes = not isQuotes
                    case 123:  # {
                        if isQuotes:
                            continue
                        depth -= 1
                        if depth == -1:
                            stack.append(pos)
                    case 125:  # }
                        if isQuotes:
                            continue
                        depth += 1
                        if depth == 0:
                            stack.append(pos)
                    case 91:  # [
                        if isQuotes:
                            continue
                        depth -= 1
                        if depth == -1:
                            stack.append(pos)
                    case 93:  # ]
                        if isQuotes:
                            continue
                        depth += 1
                        if depth == 0:
                            stack.append(pos)
                    case 40:  # (
                        if isQuotes:
                            continue
                        depth -= 1
                        if depth == -1:
                            stack.append(pos)
                    case 41:  # )
                        if isQuotes:
                            continue
                        depth += 1
                        if depth == 0:
                            stack.append(pos)

            isOpen = True
            cache = [0, 0]
            for i in stack:
                if isOpen:
                    cache[0] = i
                else:
                    cache[1] = i
                    tokens.append((cache[0], cache[1]))
                isOpen = not isOpen
            messageStart, messageEnd = tokens[1]
            return (
                jsonData[:messageStart]
                + b'"Trimmed for efficiency"'
                + jsonData[messageEnd + 1 :]
            )

        def __repr__(self):
            return f"Conversation({self.name})"

        def load(self):
            raise NotImplementedError("To be Done")
            self.isLoaded = True

    @dataclass
    class ConvoMessage:  # this will be a linked list, btw
        isMedia: bool
        _prevMessage: "ItemTemplates.ConvoMessage"
        _nextMessage: "ItemTemplates.ConvoMessage"
        time: datetime

        @property
        def prevMessage(self):
            return self._prevMessage

        @property
        def nextMessage(self):
            return self._nextMessage

        @nextMessage.setter
        def nextMessage(self, message):
            # NOTE: sanitycheck, natamad pa ko iimplement :3
            self._nextMessage = message


class Structures:
    class Metadata:
        path: Path
        def __init__(self, path):
            self.path = path

    class Messages:
        path = "your_facebook_activity/messages"

        def __init__(self, path):
            self.path = path / self.path
            
            archived = self.__parseMessageDirectory(
                self.path / "archived_threads", 
                self.path / "filtered_threads")
            self.inbox = self.__parseMessageDirectory(
                self.path / "e2ee_cutover",
                self.path / "inbox")

        @staticmethod
        def __parseMessageDirectory(*subdirs):
            result = []
            for subdir in subdirs:
                for i in subdir.iterdir():
                    name = "_".join(i.name.split("_")[:-1])
                    if name == "":
                        name = i.name
                    result.append(ItemTemplates.Conversation(subdir / i))
            return result

    class JSONDecoder(json.JSONDecoder):
        def __init__(self, *args, **kwargs):
            json.JSONDecoder.__init__(
                self, object_pairs_hook=self.object_pairs_hook, *args, **kwargs
            )

        def object_pairs_hook(self, obj):
            result = {}
            for key, value in obj:
                if isinstance(value, str):  # fix the mojibake
                    result[key] = value.encode("latin1").decode("utf-8")
                elif key == "timestamp_ms":
                    result[key] = datetime.datetime.fromtimestamp(value / 1000)
                else:
                    result[key] = value
            return result


class FacebookData:
    errorCode = 0  # TODO: documentation definitions
    rootPath = ""

    def __init__(self, path):
        # TODO: setup logging
        # there MUST be atleast your_facebook_data inside this folder
        self.rootPath = Path(path)  # TODO: sanitycheck pls
        self.Metadata = Structures.Metadata(self.rootPath)
        self.Messages = Structures.Messages(self.rootPath)


# Engine Version 1.0.0
# class Template:
#     class Folders:
#         def __init__(self, logIdentity, *args, **kwargs):
#             # path definitions
#             self.path = self.Parent.rootPath / self.identity
#             if not self.path.is_dir():
#                 raise NotADirectoryError(
#                     self.path, "Path given either does not exist or is a file."
#                 )
#             self._setupLogHandlers(logIdentity)

#         def _setupLogHandlers(self, name):
#             self.logger = logging.getLogger(name)
#             self.Parent.logstreamer.setFormatter(self.Parent.logformatter)

#             self.logger.setLevel(self.Parent.options["log"])
#             self.Parent.logstreamer.setLevel(self.Parent.options["log"])

#         def __repr__(self):
#             return f"FacebookData(/{self.identity})"

#     class Conversation(Folders):
#         def __init__(self, path, name, parent):
#             self.Parent = parent
#             self._setupLogHandlers("FacebookData.Activity.Messages.%s" % name)
#             self.path = path
#             self.internalName = name
#             self.audios = self.__getFiles(self.path / "audio")
#             self.files = self.__getFiles(self.path / "files")
#             self.gifs = self.__getFiles(self.path / "gifs")
#             self.photos = self.__getFiles(self.path / "photos")
#             self.videos = self.__getFiles(self.path / "videos")
#             self.jsonRaw = self.interpretJSONs(
#                 tuple(
#                     self.path.glob("message_*.json"),
#                 )
#             )

#             # flags
#             self.participants = []
#             for _ in self.jsonRaw["participants"]:
#                 self.participants.append(_["name"])
#             self.isGroupChat = True if len(self.participants) >= 3 else False
#             self.name = (
#                 self.jsonRaw["title"]
#                 if self.jsonRaw["title"] != ""
#                 else self.internalName
#             )
#             self.messages = self.jsonRaw["messages"]
#             self.convoLinks = self.__extractURL()
#             self.logger.debug("Conversation with %s initialized", name)

#         def interpretJSONs(self, jsonpath):
#             with jsonpath[0].open(mode="rb") as jsondata:
#                 data = json.loads(jsondata.read(), cls=Template.FacebookJSONDecoder)
#             if len(jsonpath) >= 2:
#                 for i in jsonpath[1:]:
#                     with i.open(mode="rb") as jsondata:
#                         adddata = json.loads(
#                             jsondata.read(), cls=Template.FacebookJSONDecoder
#                         )
#                         data["messages"] += adddata["messages"]
#             return data

#         def __getFiles(self, path):
#             return list(path.glob("*")) if path.is_dir() else None

#         def __extractURL(self):
#             result = []
#             convoLinkRegex = r"(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])"
#             convoLinkFilter = [
#                 "meet.google.com",
#                 "zoom.us",
#                 "us05web.zoom.us",
#                 "us04web.zoom.us",
#             ]  # this links are used for online class, as such, does not serve any useful purpose
#             for i in self.messages:
#                 if "content" not in i:
#                     continue
#                 URL = re.findall(convoLinkRegex, i["content"])
#                 if URL == []:
#                     continue
#                 for x in URL:
#                     if x[1] in convoLinkFilter:
#                         continue
#                     result.append(f"{x[0]}://{x[1]}{x[2]}")
#             return result

#         def __repr__(self):
#             return f"Conversation({self.name})"

#     class FacebookJSONDecoder(json.JSONDecoder):
#         def __init__(self, *args, **kwargs):
#             json.JSONDecoder.__init__(
#                 self, object_hook=self.object_hook, *args, **kwargs
#             )

#         def object_hook(self, obj):
#             for key, value in obj.items():
#                 if isinstance(value, str):  # fix the mojibake
#                     obj[key] = value.encode("latin1").decode("utf-8")
#                 elif key == "timestamp_ms":
#                     obj[key] = datetime.datetime.fromtimestamp(value / 1000)
#             return obj


# class FacebookData(Template.Folders):
#     identity = ""  # should be / but weird stuffs happens in Template.Folders.__init__.pathdefinitions

#     def __init__(self, root, *args, **kwargs):
#         self.Parent = self
#         self.rootPath = root
#         # argument parsings
#         self.options = {
#             "log": logging.INFO,
#         }
#         self.options.update(kwargs)
#         self._setup_logger()
#         super().__init__("FacebookData", *args, **kwargs)
#         self.logger.addHandler(self.Parent.logstreamer)
#         self.logger.debug("Logging Initialized")

#         self.Activity = FacebookActivity(self)
#         self.logger.debug("FacebookData initialized")

#     def _setup_logger(self):
#         self.logstreamer = logging.StreamHandler()
#         self.logformatter = logging.Formatter("%(levelname)s: %(name)s - %(message)s")


# class FacebookActivity(Template.Folders):
#     identity = "your_facebook_activity"

#     def __init__(self, parent):
#         self.Parent = parent
#         # breakpoint()
#         super().__init__("FacebookData.Activity")

#         self.messages = Messages(parent)
#         self.logger.debug("Activity initialized from %s", self.path)


# class Messages(Template.Folders):
#     identity = "your_facebook_activity/messages"

#     def __init__(self, parent):
#         self.Parent = parent
#         super().__init__("FacebookData.Activity.Messages")
#         # 2 types, archived, inbox
#         self.archived = self.__parseMessageDirectory(
#             "archived_threads"
#         ) + self.__parseMessageDirectory("filtered_threads")
#         self.inbox = self.__parseMessageDirectory(
#             "e2ee_cutover"
#         ) + self.__parseMessageDirectory("inbox")
#         self.logger.debug("MessageRoot initialized from %s", self.path)

#     def __parseMessageDirectory(self, subdir):
#         result = []
#         for i in (self.path / subdir).iterdir():
#             name = "_".join(i.name.split("_")[:-1])
#             if name == "":
#                 name = i.name
#             result.append(Template.Conversation(i, name, self.Parent))
#         return result


# class FacebookExceptions:
#     class InvalidDirectoryError(OSError):
#         def __init__(self, directory, message=""):
#             self.directory = directory
#             self.message = (
#                 "Path given seems to be invalid, modified, or the wrong path"
#                 if message == ""
#                 else message
#             )

#         def __str__(self):
#             return f"{self.message} ({self.directory})"


if __name__ == "__main__":
    FacebookData("A:/Cache/bonnybonnybonaktan_data")
    # run(app, host='localhost', port=42069)

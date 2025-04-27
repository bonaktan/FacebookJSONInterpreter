"""Module responsible for the Messages Interpretation
The most crucial part of this project
"""

from pathlib import Path
import json
import datetime
import warnings

PATH = Path()


class Conversation:
    """Construct for an individual conversation in messages/"""
    name = "Facebook User"
    convo = []
    path = Path()
    def __init__(self, path):
        global PATH
        PATH = Path("\\".join(path.parts[:-4]))
        assert path.exists(), f"The path given, {path}, does not exist"
        self.path = path
        with (self.path / "message_1.json").open(mode="rb") as f:
            convo_data_piece = json.loads(f.read(), cls=FacebookJSONDecoder)
            self.name = convo_data_piece["title"]
        print(f"Loaded Conversation({self.name})")

    def load(self):
        convo_data_count = len(list(self.path.glob("message_*.json")))
        for i in range(convo_data_count):
            convo_data_piece_path = self.path / f"message_{i+1}.json"
            with convo_data_piece_path.open(mode="rb") as f:
                convo_data_piece = json.loads(f.read(), cls=FacebookJSONDecoder)
                # breakpoint()
                for message in convo_data_piece["messages"]:
                    self.convo.append(ConvoData(message))

    def __repr__(self):
        return f"Conversation({self.name})"


class ConvoMedia:
    """Construct for the Conversation Media"""
    path = None
    timestamp = None
    def __init__(self, photo_data):
        self.path = photo_data.get("uri", None)
        self.timestamp = photo_data.get("creation_timestamp", None)


class ConvoData:
    """Construct for an individual Message Snippet"""
    message = None
    timestamp = None
    reaction = None
    sender = None
    media = []
    next_message = None
    prev_message = None
    def __init__(self, message):
        self.message = message.get("content", None)
        self.timestamp = message.get("timestamp_ms", None)
        self.sender = message.get("sender_name", None)

    def __repr__(self):
        if self.message is None: return ""
        return self.message


class FacebookJSONDecoder(json.JSONDecoder):
    """Custom JSON Interpreter for the Conversation JSON Files"""
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(
            self, object_hook=self.anti_mojibake, *args, **kwargs
        )

    def anti_mojibake(self, obj):
        result = {}
        for key in obj:
            value = obj[key]
            if isinstance(value, str):  # fix the mojibake
                result[key] = value.encode("latin1").decode("utf-8")
            if key == "uri":
                if value.find("https") != -1:
                    result[key] = Path(value)
                else:
                    result[key] = PATH / value
                    if not result[key].exists():
                        warnings.warn(f"The path given, {result[key]}, does not exist")
            elif key == "timestamp_ms":
                result[key] = datetime.datetime.fromtimestamp(value / 1000)
            elif key == "creation_timestamp":
                result[key] = datetime.datetime.fromtimestamp(value)
            else:
                result[key] = value
        return result


# Conversation(Path(
#         r"A:\Cache\haha\your_facebook_activity\messages\e2ee_cutover\aaronpizarras_187149938953441"
#     ))

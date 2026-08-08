# Facebook JSON Interpreter
this is a vibecoded quick application that interprets facebook data exports (in json) to a viewable message.

## Usage
`pip install -r requirements.py && python app.py`

### Notes
- you have to fully unpack the data export first before usage of this app
- append `your_facebook_activity/messages/` on the path that is being asked
- if something got borked, run `python preprocessor.py '/path/to/dump/your_facebook_activity/messages/` first, then make an issue (or have claude take a crack at it! idontmind :3), send the output of preprocessor there
import json
import re
from functools import partial

fix_mojibake_escapes = partial(
    re.compile(rb'\\u00([\da-f]{2})').sub,
    lambda m: bytes.fromhex(m[1].decode()),
)

with open('message_3.json', 'rb') as binary_data:
    repaired = fix_mojibake_escapes(binary_data.read())
data = json.loads(repaired)


with open('./message_3.json', 'w', encoding='utf-8') as newMess:
    json.dump(data, newMess, ensure_ascii=False, indent=2)
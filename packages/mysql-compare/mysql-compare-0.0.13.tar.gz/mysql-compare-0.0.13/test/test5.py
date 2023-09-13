import datetime
import json
from dataclasses import dataclass

from mysql.connector import MySQLConnection, connect


@dataclass
class Checkpoint:
    checkpoint: dict
    processed: int


json_string = '{"checkpoint": {"Abc": "2023-09-01"}, "processed": 11111}'
dct: Checkpoint = Checkpoint(**json.loads(json_string))
print(dct)

datat: list[tuple[str, str]] = [("Abc", "date")]

print(dct)

for k, v in dct.checkpoint.items():
    for coln, colt in datat:
        if k == coln:
            if colt == "date":
                dct.checkpoint[k] = datetime.datetime.strptime(v, "%Y-%m-%d")
print(dct.checkpoint)


# def read_checkpoint(self):
#     if os.path.exists(self.checkpoint_file):
#         with open(self.checkpoint_file, "r", encoding="utf8") as f:
#             return json.load(f)
#     else:
#         return None

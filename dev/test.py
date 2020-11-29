import json
a = b'\x00\x00\x00X'
i = int.from_bytes(a,byteorder='big')

b = {"type": "send", "firstname": "EIFERT", "lastname": "THOMAS", "message": "HELLO THOMAS"}
b = json.dumps(b)
b = b.encode('utf-8')

print(i)

print(len(b))
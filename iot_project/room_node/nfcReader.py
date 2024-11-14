from mfrc522 import MFRC522
import spidev
import RPi.GPIO

def write():
    blocks = [8, 9, 10]
    text = "Hello World"
    data = bytearray()
    data.extend(bytearray(text.ljust(len(blocks) * 16).encode("ascii")))
    i = 0

    for block_num in blocks:
        reader.WriteTag(block_num, data[(i*16):(i+1)*16])
        i += 1

    print("done writing")


def read():
    blocks = [8, 9, 10]
    data = []
    for block_num in blocks:
        block_data = reader.ReadTag(block_num)
        if block_data:
            data+=block_data
    if data:
        print("".join(chr(i) for i in data))

    print("done reading")

reader = MFRC522()

status = None
while status != reader.MI_OK:
    (status, TagType) = reader.Request(reader.PICC_REQIDL)
    if status == reader.MI_OK:
        print("Connection success")

(status, uid) = reader.Anticoll()
if status == reader.MI_OK:
    print(f"UID is {uid}")

reader.SelectTag(uid)

print("Authenticating...")
trailer_block = 11

key3 = [0xD3, 0xF7, 0xD3, 0xF7, 0xD3, 0xF7]

status = reader.Authenticate(reader.PICC_AUTHENT1A, trailer_block, key3, uid)


print("Done w auth")

write()
read()

reader.StopAuth()


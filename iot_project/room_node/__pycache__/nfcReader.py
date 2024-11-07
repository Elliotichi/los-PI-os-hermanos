from mfrc522 import MFRC522

reader = mfrc522()

status =  None
while status != reader.MI_OK:
	(status, TagType) = reader.Request(reader.PICC_REQIDL)
	if status == reader.MI_OK:
		print("Connection Success!")
		
(status, uid) = reader.Anticoll()
if status == reader.MI_OK:
	print(uid)
	
    reader.SelectTag(uid)

trailer_block = 11
#This is the default key for MIFARE Cards
key = [0xFF, 0xFF, 0xFF , 0xFF, 0xFF, 0xFF]
status = reader.Authenticate(
        reader.PICC_AUTHENT1A, trailer_block , key, uid)

block_nums = [8, 9, 10]
data = []
for block_num in block_nums:
	block_data = reader.ReadTag(block_num)
	if block_data:
		data += block_data
if data:
	print(''.join(chr(i) for i in data))
	
block_nums = [8, 9, 10]
text = "Hello, World"
data = bytearray()
data.extend(bytearray(text.ljust(  len(block_addrs)  *  16).encode('ascii')))
i = 0
for block_num in block_addrs:
	reader.WriteTag(block_num, data[(i*16):(i+1)*16]) 
	i +=  1
	
reader.StopAuth()

from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()


id, text = reader.read()
print(f"ID: {id}")
print(f"Text: {text}")


text = "hello_world"
id, text_written = reader.write(text)
print(f"ID: {id}")
print(f"Text Written: {text_written}")


	
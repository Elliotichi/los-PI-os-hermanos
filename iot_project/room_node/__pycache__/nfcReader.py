from mfrc522 import SimpleMFRC522 as nfc

reader = nfc()


text = "hello_world"
id, text_written = reader.write(text)
print(f"ID: {id}")
print(f"Text Written: {text_written}")
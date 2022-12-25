def Read(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        text = f.read()
    return text

def Write(file_name, text: str):
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(text)
    return 

def ReadB(file_name):
    with open(file_name, 'rb') as f:
        text = f.read()
    return text

def WriteB(file_name, blob: bytes):
    with open(file_name, 'wb') as f:
        f.write(blob)
    return 

def Read(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        text = f.read()
    return text

def Write(file_name, text):
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(text)
    return 

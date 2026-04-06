#Bai1
#_tuple = ('a','b','d','e')
#new_tuple = _tuple[:2] + ('c',) + _tuple[2:]
#print(new_tuple)
#bai2
#_tuple = ('ab','b','e','d','e','ab','c')
#new_tuple = tuple(x for x in _tuple if _tuple.count(x) == 1)
#print(new_tuple)
#bai 3
#_tuple = ('ab','b','e','d','e','ab','c')
#new_tuple = tuple(x for i, x in enumerate(_tuple) if x not in _tuple[:i])
#print(new_tuple)
#bai nang cao 
def load_key(file_path):
    with open(file_path, 'r') as file:
        key = file.read().strip()
    return key

def encrypt_file(input_file,output_file,key):
    with open(input_file, 'r' ,encoding='utf-8') as file:
        content = file.read()
    encrypted = ''
    for ch in content:
        encrypted += key.get(ch, ch)
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(encrypted)

def decrypt_file(input_file,output_file,key):
    #dao key 
    reversed_key = {v: k for k, v in key.items()}
    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()
    decrypted = ''
    for ch in content:
        decrypted += reversed_key.get(ch, ch)
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(decrypted)

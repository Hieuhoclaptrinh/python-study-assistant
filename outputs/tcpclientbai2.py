import socket

HOST = 'localhost'
PORT = 8091

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

a = input("Nhập số nguyên a: ")
b = input("Nhập số nguyên b: ")
msg = f"{a},{b}"

s.send(msg.encode())
print(f"Đã gửi lên server: {msg}")

data = s.recv(1024).decode()
print(f"Dữ liệu từ server: {data}")

s.close()

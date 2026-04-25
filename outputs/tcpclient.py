import socket

HOST = 'localhost'
PORT = 8090

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

msg = "From CLIENT TCP"
s.send(msg.encode())
print(f"Đã gửi lên server: {msg}")

data = s.recv(1024).decode()
print(f"Thông điệp nhận từ server: {data}")

s.close()

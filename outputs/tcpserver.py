import socket

HOST = 'localhost'
PORT = 8090

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()

print(f"Server đang lắng nghe tại {HOST}:{PORT}")

while True:
    conn, addr = s.accept()
    print('Đã kết nối từ', addr)

    data = conn.recv(1024).decode()
    if not data:
        conn.close()
        continue

    print(f"Thông điệp nhận được từ client: {data}")

    reply = "From SERVER TCP"
    conn.send(reply.encode())
    print(f"Đã gửi về client: {reply}")

    conn.close()

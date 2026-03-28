print("Bài 1: Tính tổng hai số")
a = int(input("Nhập số thứ nhất: "))
b = int(input("Nhập số thứ hai: "))
print(f"Tổng của {a} và {b} là: {a + b}")

print("\nBài 2: In chuỗi ký tự")
s = input("Nhập chuỗi ký tự: ")
print(f"Chuỗi vừa nhập: {s}")

print("\nBài 3: Tính toán với ba số")
x = int(input("Nhập số thứ nhất: "))
y = int(input("Nhập số thứ hai: "))
z = int(input("Nhập số thứ ba: "))
print(f"Tổng: {x + y + z}")
print(f"Tích: {x * y * z}")
print(f"Hiệu của {x} và {y}: {x - y}")
print(f"Hiệu của {y} và {z}: {y - z}")
print(f"Hiệu của {x} và {z}: {x - z}")
print(f"Phép chia lấy phần nguyên của {x} và {y}: {x // y}")
print(f"Phép chia lấy phần dư của {x} và {y}: {x % y}")
print(f"Kết quả chính xác của {x} và {y}: {x / y}")

print("\nBài 4: Ghép chuỗi ký tự")
s1 = input("Nhập chuỗi thứ nhất: ")
s2 = input("Nhập chuỗi thứ hai: ")
s3 = input("Nhập chuỗi thứ ba: ")
print(f"Chuỗi ghép: {s1} {s2} {s3}")

print("\nBài 5: Tính chu vi và diện tích hình tròn")
R = float(input("Nhập bán kính: "))
pi = 3.14
CV = 2 * R * pi
DT = pi * R * R
print(f"Chu vi: {CV}")
print(f"Diện tích: {DT}")
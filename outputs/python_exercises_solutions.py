import math

# Bài 1: Tính tổng hai số nguyên
num1 = int(input('Nhập số thứ nhất: '))
num2 = int(input('Nhập số thứ hai: '))
total = num1 + num2
print(f'Tổng của {num1} và {num2} là: {total}')

# Bài 2: In chuỗi ký tự
string = input('Nhập chuỗi ký tự: ')
print(string)

# Bài 3: Tính toán ba số nguyên
num1 = int(input('Nhập số thứ nhất: '))
num2 = int(input('Nhập số thứ hai: '))
num3 = int(input('Nhập số thứ ba: '))
print(f'Tổng và tích của ba số là: {num1+num2+num3} và {num1*num2*num3}')
a, b = num1, num2
print(f'Hiệu của {a} và {b} là: {a-b}')
print(f'Phép chia lấy phần nguyên của {a} và {b} là: {a//b}, dư: {a%b}, kết quả chính xác: {a/b}')

# Bài 4: Ghép ba chuỗi ký tự
str1 = input('Nhập chuỗi thứ nhất: ')
str2 = input('Nhập chuỗi thứ hai: ')
str3 = input('Nhập chuỗi thứ ba: ')
print(f'Chuỗi ghép: {str1} {str2} {str3}')

# Bài 5: Tính chu vi và diện tích hình tròn
radius = float(input('Nhập bán kính: '))
CV = 2 * math.pi * radius
DT = math.pi * radius ** 2
print(f'Chu vi: {CV:.2f}, Diện tích: {DT:.2f}')
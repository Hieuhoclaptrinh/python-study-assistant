n = int(input('nhap 1 so nguyen duong: '))
if n % 2 == 0 and n % 3 == 0:
    print("so chia het cho 2 va 3")
elif n % 2 == 0:
    print("so chia het cho 2")
elif n % 3 == 0:
    print("so chia het cho 3")
else:
    print("so khong chia het cho 2 va 3")


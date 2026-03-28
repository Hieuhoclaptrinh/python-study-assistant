def bai_1():
    a = int(input('Nhap so nguyen thu nhat: '))
    b = int(input('Nhap so nguyen thu hai: '))
    tong = a + b
    print('Tong hai so:', tong)


def bai_2():
    chuoi = input('Nhap chuoi ky tu: ')
    print('Chuoi ky tu:', chuoi)


def bai_3():
    a = int(input('Nhap so nguyen thu nhat: '))
    b = int(input('Nhap so nguyen thu hai: '))
    c = int(input('Nhap so nguyen thu ba: '))
    tong = a + b + c
    tich = a * b * c
    print('Tong:', tong)
    print('Tich:', tich)
    hieu = a - b  # Giả sử lấy hiệu của a và b
    print('Hieu:', hieu)
    if b != 0:
        chia_nguyen = a // b
        chia_du = a % b
        chia_chinh_xac = a / b
        print('Chia nguyen:', chia_nguyen)
        print('Chia du:', chia_du)
        print('Chia chinh xac:', chia_chinh_xac)
    else:
        print('Khong the chia cho 0')


def bai_4():
    chuoi1 = input('Nhap chuoi ky tu thu nhat: ')
    chuoi2 = input('Nhap chuoi ky tu thu hai: ')
    chuoi3 = input('Nhap chuoi ky tu thu ba: ')
    ket_qua = chuoi1 + ' ' + chuoi2 + ' ' + chuoi3
    print('Chuoi ghep:', ket_qua)


def bai_5():
    import math
    R = float(input('Nhap ban kinh: '))
    CV = 2 * R * math.pi
    DT = math.pi * R * R
    print('Chu vi:', CV)
    print('Dien tich:', DT)


# Chạy các bài tập
bai_1()
bai_2()
bai_3()
bai_4()
bai_5()
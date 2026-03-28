def bai_1():
    so_nguyen = int(input('Nhap vao mot so nguyen duong: '))
    if so_nguyen % 2 == 0:
        print('Day la mot so chan')
    else:
        print('Day la mot so le')


def bai_2():
    a = int(input('Nhap vao canh a: '))
    b = int(input('Nhap vao canh b: '))
    c = int(input('Nhap vao canh c: '))
    if a + b > c and a + c > b and b + c > a:
        print('Do dai ba canh tam giac')
    else:
        print('Day khong phai do dai ba canh tam giac')


def bai_3():
    nam_sinh = int(input('Nhap vao nam sinh: '))
    from datetime import datetime
    nam_hien_tai = datetime.now().year
    tuoi = nam_hien_tai - nam_sinh
    print(f'Nam sinh {nam_sinh}, vay ban {tuoi} tuoi.')


if __name__ == '__main__':
    bai_1()
    bai_2()
    bai_3()
def check_even_odd():
    number = int(input('Nhap vao mot so nguyen duong: '))
    if number % 2 == 0:
        print('Day la mot so chan')
    else:
        print('Day la mot so le')


def check_triangle():
    a = int(input('Nhap vao canh a: '))
    b = int(input('Nhap vao canh b: '))
    c = int(input('Nhap vao canh c: '))
    if a + b > c and a + c > b and b + c > a:
        print('Do dai ba canh tam giac')
    else:
        print('Day khong phai do dai ba canh tam giac')


def calculate_age():
    birth_year = int(input('Nhap vao nam sinh: '))
    current_year = 2023
    age = current_year - birth_year
    print(f'Nam sinh {birth_year}, vay ban {age} tuoi.')

check_even_odd()
check_triangle()
calculate_age()
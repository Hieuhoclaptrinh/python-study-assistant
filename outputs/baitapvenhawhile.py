tich = 1
i = 1 
while i <= 10:
    tich = tich * i
    i += 1
    print("Tich la: ", tich)
    
    ##day la bai 1

## day la bai 2
n = int(input("Nhap n: "))
giai_thua = 1
i = 1
while i <= n:
    giai_thua = giai_thua * i
    i += 1  
    print("Giai thua la: ", giai_thua)
    

    ## day la bai 3
n = int(input("Nhap n: "))

if n < 2:
    print("Khong phai la so nguyen to")
else:
    i = 2
    la_so_nguyen_to = True

    while i <n :
        if n % i == 0:
            la_so_nguyen_to = False
            break
        i += 1
    if la_so_nguyen_to:
        print("La so nguyen to")
    else:        print("Khong phai la so nguyen to")

## day la bai 4
n = int(input("Nhap n: "))
tong = 0
i = 0
while i < n:
    if i % 2 == 0:
        tong  = tong + i
    i += 1
    print("Tong cac so chan nho hon", n, "la:", tong)
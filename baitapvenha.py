email = input("Nhập email của bạn: ")
skype = input("Nhập skype của bạn: ")
dia_chi = input("Nhập địa chỉ của bạn: ")
noi_lam_viec = input("Nhập nơi làm việc của bạn: ")
# luu thông tin vào file
with open("thong_tin.txt", "w") as file:
    file.write("Email: " + email + "\n")
    file.write("Skype: " + skype + "\n")
    file.write("Địa chỉ: " + dia_chi + "\n")
    file.write("Nơi làm việc: " + noi_lam_viec + "\n")
    print("Thông tin đã được lưu vào file thong_tin.txt")
# Đọc từ file setInfo.txt và hiển thị ra màn hình
print("\nThông tin đọc từ file:")
with open("setInfo.txt", "r", encoding="utf-8") as f:
    noi_dung = f.read()
    print(noi_dung)
 

 #bai5

file_name = "demo_file2.txt"
#tao mau file
with open(file_name, "w", encoding="utf-8") as file:
   f.write("Dem so luong tu xuat hien abc abc abc 12 12 it it eaut")

# Đọc nội dung file
with open(file_name, "r", encoding="utf-8") as file:
    noi_dung = file.read()
    print("Nội dung file:", noi_dung)

    #tach tu va dem
    words = noi_dung.split()
    result = {}

    for word in words:
        if word in result:
            result[word] += 1
        else:
            result[word] = 1

    print("Số lượng từ xuất hiện:")
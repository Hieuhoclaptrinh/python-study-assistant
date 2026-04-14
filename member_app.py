import re
import sqlite3
import sys
from typing import Optional

from PyQt5 import QtCore, QtWidgets


DB_NAME = "members.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ho TEXT NOT NULL,
            ten TEXT NOT NULL,
            phone TEXT NOT NULL,
            password TEXT NOT NULL,
            ngay INTEGER NOT NULL,
            thang INTEGER NOT NULL,
            nam INTEGER NOT NULL,
            gioi_tinh TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def password_is_strong(password: str):
    if len(password) < 8:
        return False, "Mật khẩu phải có ít nhất 8 ký tự."
    if not re.search(r"[a-z]", password):
        return False, "Mật khẩu phải có ít nhất 1 chữ thường a-z."
    if not re.search(r"[A-Z]", password):
        return False, "Mật khẩu phải có ít nhất 1 chữ in hoa A-Z."
    if not re.search(r"[0-9]", password):
        return False, "Mật khẩu phải có ít nhất 1 chữ số 0-9."
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", password):
        return False, "Mật khẩu phải có ít nhất 1 ký tự đặc biệt."
    return True, ""


class RegisterFormBase(QtWidgets.QDialog):
    def __init__(self, title="Đăng ký thành viên", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(620, 620)
        self.setup_ui()

    def setup_ui(self):
        self.lbl_title = QtWidgets.QLabel("ĐĂNG KÝ", self)
        self.lbl_title.setGeometry(30, 20, 150, 30)
        font = self.lbl_title.font()
        font.setPointSize(16)
        font.setBold(True)
        self.lbl_title.setFont(font)

        self.lbl_subtitle = QtWidgets.QLabel("Nhanh chóng và dễ dàng", self)
        self.lbl_subtitle.setGeometry(30, 55, 250, 20)

        self.txt_ho = QtWidgets.QLineEdit(self)
        self.txt_ho.setGeometry(30, 95, 250, 35)
        self.txt_ho.setPlaceholderText("Họ")

        self.txt_ten = QtWidgets.QLineEdit(self)
        self.txt_ten.setGeometry(310, 95, 250, 35)
        self.txt_ten.setPlaceholderText("Tên")

        self.txt_phone = QtWidgets.QLineEdit(self)
        self.txt_phone.setGeometry(30, 145, 530, 35)
        self.txt_phone.setPlaceholderText("Số điện thoại")

        self.txt_password = QtWidgets.QLineEdit(self)
        self.txt_password.setGeometry(30, 195, 530, 35)
        self.txt_password.setPlaceholderText("Mật khẩu")
        self.txt_password.setEchoMode(QtWidgets.QLineEdit.Password)

        self.lbl_birth = QtWidgets.QLabel("Ngày sinh", self)
        self.lbl_birth.setGeometry(30, 245, 150, 25)

        self.cbo_day = QtWidgets.QComboBox(self)
        self.cbo_day.setGeometry(30, 275, 100, 35)
        self.cbo_day.addItems([str(i) for i in range(1, 32)])

        self.cbo_month = QtWidgets.QComboBox(self)
        self.cbo_month.setGeometry(150, 275, 150, 35)
        self.cbo_month.addItems([f"Tháng {i}" for i in range(1, 13)])

        self.cbo_year = QtWidgets.QComboBox(self)
        self.cbo_year.setGeometry(320, 275, 120, 35)
        self.cbo_year.addItems([str(i) for i in range(1990, 2011)])

        self.lbl_gender = QtWidgets.QLabel("Giới tính", self)
        self.lbl_gender.setGeometry(30, 330, 100, 25)

        self.radio_nam = QtWidgets.QRadioButton("Nam", self)
        self.radio_nam.setGeometry(30, 360, 80, 25)

        self.radio_nu = QtWidgets.QRadioButton("Nữ", self)
        self.radio_nu.setGeometry(130, 360, 80, 25)

        self.lbl_terms = QtWidgets.QLabel(self)
        self.lbl_terms.setGeometry(30, 400, 530, 110)
        self.lbl_terms.setWordWrap(True)
        self.lbl_terms.setText(
            "Bằng cách nhấn vào Đăng ký, bạn đồng ý với Điều khoản, "
            "Chính sách dữ liệu và Chính sách cookie của chúng tôi.\n\n"
            "Bạn cam kết cung cấp thông tin chính xác, bảo mật tài khoản, "
            "không sử dụng hệ thống sai mục đích và đồng ý với chính sách bảo mật."
        )

        self.chk_terms = QtWidgets.QCheckBox("Tôi đồng ý với các điều khoản trên", self)
        self.chk_terms.setGeometry(30, 520, 300, 25)

        self.btn_submit = QtWidgets.QPushButton("Đăng ký", self)
        self.btn_submit.setGeometry(240, 565, 120, 35)

    def get_form_data(self):
        if self.radio_nam.isChecked():
            gioi_tinh = "Nam"
        elif self.radio_nu.isChecked():
            gioi_tinh = "Nữ"
        else:
            gioi_tinh = ""

        return {
            "ho": self.txt_ho.text().strip(),
            "ten": self.txt_ten.text().strip(),
            "phone": self.txt_phone.text().strip(),
            "password": self.txt_password.text(),
            "ngay": int(self.cbo_day.currentText()),
            "thang": int(self.cbo_month.currentText().replace("Tháng ", "")),
            "nam": int(self.cbo_year.currentText()),
            "gioi_tinh": gioi_tinh,
            "dong_y": self.chk_terms.isChecked(),
        }

    def validate_form(self):
        data = self.get_form_data()
        if not data["ho"]:
            return False, "Bạn chưa nhập Họ."
        if not data["ten"]:
            return False, "Bạn chưa nhập Tên."
        if not data["phone"]:
            return False, "Bạn chưa nhập Số điện thoại."
        if not data["password"]:
            return False, "Bạn chưa nhập Mật khẩu."
        if not data["gioi_tinh"]:
            return False, "Bạn chưa chọn Giới tính."
        if not data["dong_y"]:
            return False, "Bạn phải xác nhận đồng ý với các điều khoản."

        ok, msg = password_is_strong(data["password"])
        if not ok:
            return False, msg

        return True, ""


class RegisterDialog(RegisterFormBase):
    def __init__(self):
        super().__init__(title="Đăng ký thành viên")
        self.btn_submit.clicked.connect(self.handle_register)

    def handle_register(self):
        valid, message = self.validate_form()
        if not valid:
            QtWidgets.QMessageBox.warning(self, "Lỗi", message)
            return

        data = self.get_form_data()
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO members (ho, ten, phone, password, ngay, thang, nam, gioi_tinh)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["ho"],
                data["ten"],
                data["phone"],
                data["password"],
                data["ngay"],
                data["thang"],
                data["nam"],
                data["gioi_tinh"],
            ),
        )
        conn.commit()
        conn.close()

        QtWidgets.QMessageBox.information(self, "Thành công", "Đăng ký thành công.")
        self.hide()
        self.member_list = MemberListDialog()
        self.member_list.show()


class EditMemberDialog(RegisterFormBase):
    def __init__(self, member_id: int, parent=None):
        super().__init__(title="Sửa thông tin thành viên", parent=parent)
        self.member_id = member_id
        self.btn_submit.setText("Lưu thay đổi")
        self.btn_submit.clicked.connect(self.handle_update)
        self.load_member_data()

    def load_member_data(self):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            "SELECT ho, ten, phone, password, ngay, thang, nam, gioi_tinh FROM members WHERE id = ?",
            (self.member_id,),
        )
        row = cur.fetchone()
        conn.close()

        if not row:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Không tìm thấy thành viên.")
            self.reject()
            return

        ho, ten, phone, password, ngay, thang, nam, gioi_tinh = row
        self.txt_ho.setText(ho)
        self.txt_ten.setText(ten)
        self.txt_phone.setText(phone)
        self.txt_password.setText(password)
        self.cbo_day.setCurrentText(str(ngay))
        self.cbo_month.setCurrentText(f"Tháng {thang}")
        self.cbo_year.setCurrentText(str(nam))
        if gioi_tinh == "Nam":
            self.radio_nam.setChecked(True)
        else:
            self.radio_nu.setChecked(True)
        self.chk_terms.setChecked(True)

    def handle_update(self):
        valid, message = self.validate_form()
        if not valid:
            QtWidgets.QMessageBox.warning(self, "Lỗi", message)
            return

        data = self.get_form_data()
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE members
            SET ho = ?, ten = ?, phone = ?, password = ?, ngay = ?, thang = ?, nam = ?, gioi_tinh = ?
            WHERE id = ?
            """,
            (
                data["ho"],
                data["ten"],
                data["phone"],
                data["password"],
                data["ngay"],
                data["thang"],
                data["nam"],
                data["gioi_tinh"],
                self.member_id,
            ),
        )
        conn.commit()
        conn.close()

        QtWidgets.QMessageBox.information(self, "Thành công", "Cập nhật thành công.")
        self.accept()


class MemberListDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Xem danh sách thành viên")
        self.resize(850, 500)
        self.setup_ui()
        self.load_members()

    def setup_ui(self):
        self.lbl_title = QtWidgets.QLabel("DANH SÁCH THÀNH VIÊN", self)
        self.lbl_title.setGeometry(20, 15, 300, 30)
        font = self.lbl_title.font()
        font.setPointSize(14)
        font.setBold(True)
        self.lbl_title.setFont(font)

        self.table = QtWidgets.QTableWidget(self)
        self.table.setGeometry(20, 60, 810, 340)
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Họ", "Tên", "Số điện thoại", "Ngày sinh", "Giới tính", "Mật khẩu"]
        )
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 120)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 140)
        self.table.setColumnWidth(4, 140)
        self.table.setColumnWidth(5, 100)

        self.btn_add = QtWidgets.QPushButton("Thêm mới", self)
        self.btn_add.setGeometry(160, 420, 120, 35)
        self.btn_add.clicked.connect(self.open_register_again)

        self.btn_edit = QtWidgets.QPushButton("Sửa", self)
        self.btn_edit.setGeometry(310, 420, 120, 35)
        self.btn_edit.clicked.connect(self.edit_member)

        self.btn_delete = QtWidgets.QPushButton("Xóa", self)
        self.btn_delete.setGeometry(460, 420, 120, 35)
        self.btn_delete.clicked.connect(self.delete_member)

        self.btn_refresh = QtWidgets.QPushButton("Làm mới", self)
        self.btn_refresh.setGeometry(610, 420, 120, 35)
        self.btn_refresh.clicked.connect(self.load_members)

    def load_members(self):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            "SELECT id, ho, ten, phone, ngay, thang, nam, gioi_tinh, password FROM members ORDER BY id DESC"
        )
        rows = cur.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            member_id, ho, ten, phone, ngay, thang, nam, gioi_tinh, password = row_data
            display_values = [
                str(member_id),
                ho,
                ten,
                phone,
                f"{ngay:02d}/{thang:02d}/{nam}",
                gioi_tinh,
                password,
            ]
            for col_idx, value in enumerate(display_values):
                self.table.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(value))

    def get_selected_member_id(self) -> Optional[int]:
        current_row = self.table.currentRow()
        if current_row < 0:
            QtWidgets.QMessageBox.warning(self, "Thông báo", "Vui lòng chọn 1 thành viên.")
            return None

        item = self.table.item(current_row, 0)
        if item is None:
            QtWidgets.QMessageBox.warning(self, "Thông báo", "Không lấy được ID thành viên.")
            return None

        return int(item.text())

    def delete_member(self):
        member_id = self.get_selected_member_id()
        if member_id is None:
            return

        reply = QtWidgets.QMessageBox.question(
            self,
            "Xác nhận xóa",
            "Bạn có chắc muốn xóa thành viên này không?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        )
        if reply != QtWidgets.QMessageBox.Yes:
            return

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("DELETE FROM members WHERE id = ?", (member_id,))
        conn.commit()
        conn.close()

        QtWidgets.QMessageBox.information(self, "Thành công", "Xóa thành viên thành công.")
        self.load_members()

    def edit_member(self):
        member_id = self.get_selected_member_id()
        if member_id is None:
            return

        dialog = EditMemberDialog(member_id, self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.load_members()

    def open_register_again(self):
        self.register_dialog = RegisterDialog()
        self.register_dialog.show()
        self.close()


if __name__ == "__main__":
    init_db()
    app = QtWidgets.QApplication(sys.argv)
    window = RegisterDialog()
    window.show()
    sys.exit(app.exec_())

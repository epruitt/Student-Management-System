from idlelib.help_about import AboutDialog
from sqlite3 import connect

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget, QGridLayout, \
    QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QComboBox, QToolBar, QStatusBar, \
    QMessageBox
import sys
import sqlite3

class DatabaseConnection:
    def __init__(self, database_file="database.db"):
        self.database_file = database_file

    def connect(self):
        connection = sqlite3.connect(self.database_file)
        return connection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800,600)

        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        add_stu_action = QAction(QIcon("icons/add.png"),"Add Student",self)
        add_stu_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_stu_action)

        about_action = QAction(" About",self)
        help_menu_item.addAction(about_action)
        about_action.setMenuRole(QAction.MenuRole.NoRole)
        about_action.triggered.connect(self.about)

        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID","Name","Course","Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)
        self.load_data()

        #create toolbar and add elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_stu_action)
        toolbar.addAction(search_action)

        #Create status bar and add status bar elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        #Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_btn = QPushButton("Edit Record")
        edit_btn.clicked.connect(self.edit)

        delete_btn = QPushButton("Delete Record")
        delete_btn.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_btn)
        self.statusbar.addWidget(delete_btn)


    def load_data(self):
        connection = DatabaseConnection.connect()
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0)
        for row_num, row_data in enumerate(result):
            self.table.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(data)))
        connection.close()


    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()

class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add Student Name
        self.stu_name = QLineEdit()
        self.stu_name.setPlaceholderText("Name")
        layout.addWidget(self.stu_name)

        #Add drop down box of courses
        self.course_name = QComboBox()
        courses = ["Biology","Math","Astronomy", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        #add mobile
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        #add submit button
        btn = QPushButton("Register")
        btn.clicked.connect(self.add_student)
        layout.addWidget(btn)

        self.setLayout(layout)

    def add_student(self):
        name = self.stu_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course,mobile) VALUES(?, ?, ?)", (name,course,mobile))
        connection.commit()
        cursor.close()
        connection.close()
        sms.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        # Create layout and input
        layout = QVBoxLayout()
        self.stu_name = QLineEdit()
        self.stu_name.setPlaceholderText("Student Name")
        layout.addWidget(self.stu_name)

        # Create submit button
        btn = QPushButton("Search")
        btn.clicked.connect(self.search)
        layout.addWidget(btn)

        self.setLayout(layout)


    def search(self):
        name = self.stu_name.text()
        connection = DatabaseConnection.connect()
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM students WHERE name=?",(name,))
        row = list(result)
        print(row)
        items = sms.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            print(item)
            sms.table.item(item.row(),1).setSelected(True)


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()
        # get Student Name from selected row
        index = sms.table.currentRow()
        stu_name = sms.table.item(index,1).text()

        #get ID from selected row
        self.stu_id = sms.table.item(index,0).text()

        self.stu_name = QLineEdit(stu_name)
        self.stu_name.setPlaceholderText("Name")
        layout.addWidget(self.stu_name)

        # drop down box of courses
        course_name = sms.table.item(index,2).text()
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        # mobile
        mobile = sms.table.item(index,3).text()
        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # add update button
        btn = QPushButton("Update")
        btn.clicked.connect(self.update_student)
        layout.addWidget(btn)

        self.setLayout(layout)

    def update_student(self):
        connection = DatabaseConnection.connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?",
                       (self.stu_name.text(),
                        self.course_name.itemText(self.course_name.currentIndex()),
                        self.mobile.text(),
                        self.stu_id))
        connection.commit()
        cursor.close()
        connection.close()

        #resfresh the table
        sms.load_data()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")

        layout = QGridLayout()
        confirm = QLabel("Are you sure you want to delete")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirm,0,0,1,2)
        layout.addWidget(yes,1,0)
        layout.addWidget(no,1,1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)


    def delete_student(self):
        #get selected student ID and current row
        index = sms.table.currentRow()
        stu_id = sms.table.item(index,0).text()

        connection = DatabaseConnection.connect()
        cursor = connection.cursor()
        cursor.execute("DELETE from students Where id = ?", (stu_id,))
        connection.commit()
        cursor.close()
        connection.close()
        sms.load_data()

        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setWindowTitle("The record was deleted successfully!")
        confirmation_widget.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")

        content = """
        This app was created for learning Python and Portfolio Work. 
        
        Feel free to modify and reuse this app.
        """

        self.setText(content)

app = QApplication(sys.argv)
sms= MainWindow()
sms.show()
sys.exit(app.exec())
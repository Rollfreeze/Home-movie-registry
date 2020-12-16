from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import *

import sys
import sqlite3

import requests
from bs4 import BeautifulSoup
import csv

from xlsxwriter.workbook import Workbook

class SqliteHelper:
    def __init__ (self, name=None):
        self.conn = None
        self.cursor = None
        if name:
            self.open(name)
        
    def open(self, name):
        try:
            self.conn = sqlite3.connect(name)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print("Failed connecting to database...")

    def create_table(self):
        c = self.cursor
        c.execute("""CREATE TABLE movies(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Фильм TEXT NOT NULL,
                    Год INTEGER,
                    Студия TEXT NOT NULL,
                    Жанр TEXT NOT NULL,
                    Режисер TEXT NOT NULL,
                    Длительность INTEGER,
                    Возраст TEXT NOT NULL,
                    Просмотры INTEGER
                )""")

    def edit(self,query):#INSERT & UPDATE
        c = self.cursor
        c.execute(query)
        self.conn.commit()

    def select(self,query):#SELECT
        c = self.cursor
        c.execute(query)
        return c.fetchall()



class First_Form(QMainWindow):
    def __init__(self):
        super(First_Form, self).__init__()
        loadUi('main_form.ui', self) #название твоей формы из QT
        #database = SqliteHelper("test.db")
        self.loadData()
        self.show() #show the form

        self.URL = 'https://ru.wikipedia.org/wiki/250_%D0%BB%D1%83%D1%87%D1%88%D0%B8%D1%85_%D1%84%D0%B8%D0%BB%D1%8C%D0%BC%D0%BE%D0%B2_%D0%BF%D0%BE_%D0%B2%D0%B5%D1%80%D1%81%D0%B8%D0%B8_IMDb'
        self.FILE_EXCEL = 'TOP_250_MOVIE.csv'

        self.tableWidget.setColumnWidth(8,90)
        self.tableWidget.setColumnWidth(1,210)
        self.tableWidget.setColumnWidth(4,100)
        self.tableWidget.setColumnWidth(5,150)
        self.tableWidget.setColumnWidth(5,150)

        self.movie_add.clicked.connect(self.input_form_open)
        self.delete_position.clicked.connect(self.delete_user)
        self.show_movie.clicked.connect(self.loadData)
        self.movie_search.clicked.connect(self.search_by_name)
        self.studio_button.clicked.connect(self.search_by_studio)
        self.year_button.clicked.connect(self.search_by_year)
        self.genre_button.clicked.connect(self.search_by_genre)

        self.excel_button.clicked.connect(self.to_excel)

        self.excel_button_top.clicked.connect(self.parse)

    def get_html(self, url, params=None):
        r = requests.get(url, params=params)
        return r

    def get_pages_count(self, html):
        return int(10)

    def get_content(self, html):
        soup = BeautifulSoup(html, 'html.parser')

        data = soup.find_all('table')[1]

        top_sto_movies = []

        rows = data.find_all('tr')
        
        for row in rows:
            columns = row.find_all('td')
            i = 0

            place = ''
            name = ''
            year = ''
            autor = ''
            janr = ''

            for column in columns:
                if i == 0:
                    place = column.text
                    # print(place)
                if i == 1:
                    name = column.text
                if i == 2:
                    year = column.text
                if i == 3:
                    autor = column.text
                if i == 4:
                    janr = column.text
                    janr = janr.replace("\n", "")
                i = i + 1
            
            top_sto_movies.append({
                'place': place,
                'name': name,
                'year': year,
                'compositor': autor,
                'janr': janr
                })
            
        
        top_sto_movies = top_sto_movies[1:]

        return(top_sto_movies)


    def save_file(self, items, path):
        with open(path, 'w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['Место', 'Название', 'Год', 'Режисер', 'Жанр'])
            for item in items:
                writer.writerow([item['place'],
                item['name'],
                item['year'],
                item['compositor'],
                item['janr'],])

    def parse(self):
        html = self.get_html(self.URL)
        if html.status_code == 200:

            top_sto_movies = self.get_content(html.text)

            print(f'Получено {len(top_sto_movies)} Фильмов')
            
            try:
                self.save_file(top_sto_movies, self.FILE_EXCEL)
            except:
                print('Закройте обрабатываемый файл')
        else:
            print('Couldnt get html')

    def to_excel(self):
        workbook = Workbook('movies.xlsx')
        worksheet = workbook.add_worksheet()

        conn=sqlite3.connect('test.db')
        c=conn.cursor()
        c.execute("select * from movies")
        mysel=c.execute("select * from movies")
        
        worksheet.write(0, 0, 'id')
        worksheet.write(0, 1, 'Фильм')
        worksheet.write(0, 2, 'Год')
        worksheet.write(0, 3, 'Студия')
        worksheet.write(0, 4, 'Жанр')
        worksheet.write(0, 5, 'Режисер')
        worksheet.write(0, 6, 'Длительность')
        worksheet.write(0, 7, 'Возраст')
        worksheet.write(0, 8, 'Просмотры')

        for i, row in enumerate(mysel):
            print(row)
            worksheet.write(i+1, 0, row[0])
            worksheet.write(i+1, 1, row[1])
            worksheet.write(i+1, 2, row[2])
            worksheet.write(i+1, 3, row[3])
            worksheet.write(i+1, 4, row[4])
            worksheet.write(i+1, 5, row[5])
            worksheet.write(i+1, 6, row[6])
            worksheet.write(i+1, 7, row[7])
            worksheet.write(i+1, 8, row[8])
        workbook.close()

    def search_by_genre(self):
        self.clear_data()

        request_text = str(self.lineEdit.text())

        helper = SqliteHelper("test.db")
        movies = helper.select("""SELECT * FROM movies WHERE Жанр='{}'""".format(request_text))
        
        for row_number,movies in enumerate(movies):
            self.tableWidget.insertRow(row_number)
            for column_number,data in enumerate(movies):
                cell = QtWidgets.QTableWidgetItem(str(data))
                self.tableWidget.setItem(row_number,column_number,cell)

    def search_by_studio(self):
        self.clear_data()

        request_text = str(self.lineEdit.text())

        helper = SqliteHelper("test.db")
        movies = helper.select("""SELECT * FROM movies WHERE Студия='{}'""".format(request_text))
        
        for row_number,movies in enumerate(movies):
            self.tableWidget.insertRow(row_number)
            for column_number,data in enumerate(movies):
                cell = QtWidgets.QTableWidgetItem(str(data))
                self.tableWidget.setItem(row_number,column_number,cell)

    def search_by_year(self):
        self.clear_data()

        request_text = str(self.lineEdit.text())

        helper = SqliteHelper("test.db")
        movies = helper.select("""SELECT * FROM movies WHERE Год='{}'""".format(request_text))
        
        for row_number,movies in enumerate(movies):
            self.tableWidget.insertRow(row_number)
            for column_number,data in enumerate(movies):
                cell = QtWidgets.QTableWidgetItem(str(data))
                self.tableWidget.setItem(row_number,column_number,cell)

    def search_by_name(self):
        self.clear_data()

        request_text = str(self.lineEdit.text())

        helper = SqliteHelper("test.db")
        movies = helper.select("""SELECT * FROM movies WHERE Фильм='{}'""".format(request_text))
        
        for row_number,movies in enumerate(movies):
            self.tableWidget.insertRow(row_number)
            for column_number,data in enumerate(movies):
                cell = QtWidgets.QTableWidgetItem(str(data))
                self.tableWidget.setItem(row_number,column_number,cell)

    def get_selected_row_id(self):
        return self.tableWidget.currentRow()
    
    def get_selected_user_id(self):
        return self.tableWidget.item(self.get_selected_row_id(), 0).text()

    def delete_user(self):
        helper = SqliteHelper("test.db")
        try:
            id_delete = self.get_selected_user_id()
            helper.edit("DELETE FROM movies WHERE id ="+id_delete)
            self.clear_data()
            self.loadData()
        except:
            self.ShowDialog = show_dialog_form()
            self.ShowDialog.label.setText('Ошибка удаления!')
            self.ShowDialog.label_2.setText('Пожалуйста, выберете поле для удаления!')
            self.ShowDialog.show()

    def input_form_open(self):
        self.second = Input_Form()
        self.second.show()

    def clear_data(self):
        i= self.tableWidget.rowCount()
        while(self.tableWidget.rowCount()>0):
            self.tableWidget.removeRow(i)
            i = i - 1

    def loadData(self):
        self.clear_data()

        helper = SqliteHelper("test.db")
        movies = helper.select("SELECT * FROM movies")

        for row_number,movies in enumerate(movies):
            self.tableWidget.insertRow(row_number)
            for column_number,data in enumerate(movies):
                cell = QtWidgets.QTableWidgetItem(str(data))
                self.tableWidget.setItem(row_number,column_number,cell)

class show_dialog_form(QMainWindow):
    def __init__(self):
        super(show_dialog_form, self).__init__()
        loadUi('show_dialog.ui', self)
        self.show()
        self.pushButton.clicked.connect(self.ok)

    def ok(self):
        self.hide()

class Input_Form(QMainWindow):
    def __init__(self):
        super(Input_Form, self).__init__()
        loadUi('input_form.ui', self)
        self.show()
        self.add_button.clicked.connect(self.adding_data)
        self.close_button.clicked.connect(self.close_input_button)
        

    def close_input_button(self):
        self.hide()

    def adding_data(self, query): #method ДОБАВИТЬ
        try:
            film = self.lineEdit_movie.text()
            studio = self.comboBox_studio.currentText()
            janr = self.comboBox_janr.currentText()
            year = int(self.lineEdit_year.text())
            longtime = int(self.lineEdit_long.text())
            autor = self.lineEdit_autor.text()
            age = self.comboBox_age.currentText()
            views = int(self.lineEdit_views.text())

            checker = True
        except:
            self.ShowDialog = show_dialog_form()
            self.ShowDialog.show()
            checker = False

        database = SqliteHelper("test.db")
        First_Form_object = First_Form()

        if(checker == True):
            database.edit("""INSERT INTO movies (Фильм, Год, Студия, Жанр, Режисер, Длительность, Возраст, Просмотры) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}') """.format(film, year, studio, janr, autor, longtime, age, views))
            First_Form_object.loadData()
            self.close()

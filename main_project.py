from forms import *

database = SqliteHelper("test.db")

try:
    database.create_table()
except:
    pass


app = QApplication(sys.argv)
window = First_Form()

try:
    sys.exit(app.exec_())
except:
    print('exit')

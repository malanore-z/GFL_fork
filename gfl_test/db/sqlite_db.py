from gfl.core.context import SqliteContext


sqlite_path = "job.sqlite"


def create_table():
    with SqliteContext(sqlite_path) as (_, cursor):
        cursor.execute('''CREATE TABLE COMPANY(
                       ID INT PRIMARY KEY     NOT NULL,
                       NAME           TEXT    NOT NULL,
                       AGE            INT     NOT NULL,
                       ADDRESS        CHAR(50),
                       SALARY         REAL);''')


def insert_data():
    with SqliteContext(sqlite_path) as (_, cursor):
        cursor.execute("insert into COMPANY(ID, NAME, AGE, ADDRESS, SALARY) values (1, 'tom', 18, 'mar', 10086.0)")


def show_data():
    with SqliteContext(sqlite_path) as (_, cursor):
        ret = cursor.execute("select * from COMPANY")
        for r in ret:
            print("ID     : %d" % r[0])
            print("NAME   : %s - LEN: %d" % (r[1], len(r[1])))
            print("AGE    : %s" % r[2])
            print("ADDRESS: %s - LEN: %d" % (r[3], len(r[3])))
            print("SALARY : %.f" % r[4])


if __name__ == "__main__":
    show_data()

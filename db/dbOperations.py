import sqlite3

def clean_db(DB):
    # conn = sqlite3.connect('./data/airline_seating.db')
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    for n in range(60):
        # print("update seating set `name` = '' where `_rowid_` = %s" % (n+1,))
        c.execute("update seating set `name` = '' where `_rowid_` = %s" % (n+1,))

    c.execute("UPDATE metrics SET passengers_separated=0")
    c.execute("UPDATE metrics SET passengers_refused=0")
    conn.commit()
    conn.close()


def print_seating_plan(DB):
    # connection details
    # conn = sqlite3.connect('./data/airline_seating.db')
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    all_seats = c.execute("select * from seating")

    # create the dict, assign the row number as the key
    # and an empty list as the value
    myDict = {}
    for n in range (15):
        myDict[n+1] = []

    # fill the dict with the names of people in each seat
    for row, seat, name in all_seats:
        myDict[row].append(name)

    # print the dict
    for key, values in myDict.items():
        print (values)

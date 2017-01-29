import sqlite3
import pandas as pd
from booking import *
import numpy as np


def clean_db():
    conn = sqlite3.connect('./data/airline_seating.db')
    c = conn.cursor()
    for n in range(60):
        # print("update seating set `name` = '' where `_rowid_` = %s" % (n+1,))
        c.execute("update seating set `name` = '' where `_rowid_` = %s" % (n+1,))
    conn.commit()
    conn.close()


def read_in_data():
    return pd.read_csv("./data/sample_booking.csv", sep=",", header=None)


def make_booking(Booking):
    conn = sqlite3.connect('./data/airline_seating.db')
    c = conn.cursor()
    available_seats = c.execute("select * from seating where name = ''")

    for row, seat, name in available_seats:
        # print (row, seat, name)
        for itr in np.arange(Booking.parties):
            # print("update seating set name = %s where row = %s and seat = %s " % (Booking.name, row, seat))
            c.execute("update seating set name = '%s' where row = '%s' and seat = '%s' " % (Booking.name, row, seat))
            seat, row = get_next_seat(seat, row)
        break

    conn.commit()


def get_next_seat(current_seat, row):
    seats = np.array(["A", "C", "D", "F"])
    rows = np.arange(15) + 1
    for idx, seat in enumerate(seats):
        if seat == current_seat:
            return (seats[idx + 1], row) if idx != seats.size-1 else (seats[0], row+1)
    return -1


def print_seating_plan():
    # connection details
    conn = sqlite3.connect('./data/airline_seating.db')
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



def main():

    clean_db()

    # read in the data
    df = read_in_data()

    for index, row in df.iterrows():
        # print (row[0], row[1])
        # create a booking object with the name of the booker and the amount of seats required
        a_booking = Booking(row[0], row[1])
        # make the booking
        make_booking(a_booking)

    print_seating_plan()

main()

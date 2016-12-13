import sqlite3
import pandas as pd
from booking import *
import numpy as np


def read_in_data():
    return pd.read_csv("./data/sample_booking.csv", sep=",", header=None)


def make_booking(Booking):
    conn = sqlite3.connect('./data/airline_seating.db')
    c = conn.cursor()
    available_seats = c.execute("select * from seating where name = ''")

    for row, seat, name in available_seats:
        for itr in np.arange(Booking.parties):
            print("update seating set name = %s where row = %s and seat = %s " % (Booking.name, row, seat))
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


def main():
    # read in the data
    df = read_in_data()

    # create a booking object with the name of the booker and the amount of seats required
    a_booking = Booking(df[0], df[1])

    # make the booking
    make_booking(a_booking)


main()

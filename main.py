import sqlite3
import pandas as pd
import numpy as np
import os
from model import booking
from db import dbOperations

def read_in_data(pathToFile):
    bookingsFile = pd.read_csv(pathToFile, sep=",", header=None)
    allBookings = []
    for index, row in bookingsFile.iterrows():
        nextBooking = booking.Booking(row[0],row[1])
        allBookings.append(nextBooking)

    #below is a list of booking objects,
    #containing all bookings to be made
    return allBookings

def read_db_details(pathToDB):
    conn = sqlite3.connect(pathToDB)

    #get db dimentions
    details = conn.cursor().execute("SELECT * FROM rows_cols;").fetchone()
    nrows=details[0]#number of rows in the db
    seats=details[1]#seat lettering
    numberOfSeats = nrows * len(seats)

    #get number of free seats
    names_column = conn.cursor().execute("SELECT name FROM seating;").fetchall()
    freeSeats=0
    for entry in names_column:
        if entry == ('',):
            freeSeats+=1

    #create a dict, fill it with this methods results and return it
    dbDetails = {}
    dbDetails["nrows"]=nrows
    dbDetails["seatLettering"]=seats
    dbDetails["numberOfSeats"]=numberOfSeats
    dbDetails["freeSeats"]=freeSeats

    return dbDetails


def make_booking(Booking):
    conn = sqlite3.connect('./data/airline_seating.db')
    c = conn.cursor()
    available_seats = c.execute("select * from seating where name = ''")

    for row, seat, name in available_seats:
        print ("Available seats:", row, seat, name)
        for itr in np.arange(Booking.parties):
            # print("update seating set name = %s where row = %s and seat = %s " % (Booking.name, row, seat))
            c.execute("update seating set name = '%s' where row = '%s' and seat = '%s' " % (Booking.name, row, seat))
            seat, row = get_next_seat(seat, row)
            print("Gen next seat:", seat, row)
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

    #when runnign in terminal, clear the screen
    #os.system('cls')#for windows
    os.system('clear')#for linux based os

    #clean the db's exsiting entries
    dbOperations.clean_db()

    dbDetails = read_db_details('data/airline_seating.db')


    # read in the data
    df = read_in_data("data/sample_bookings.csv")


    #for index, row in df.iterrows():
        # create a booking object with the name of the booker and the amount of seats required
        #a_booking = booking.Booking(row[0], row[1])

        # make the booking
        #make_booking(a_booking)


    #dbOperations.print_seating_plan()

main()

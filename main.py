import sqlite3
import pandas as pd
import numpy as np
import os
from model import booking
from db import dbOperations



def read_in_data(pathToFile):
    df = pd.read_csv(pathToFile, sep=",", header=None)
    bookings = []

    for row in df:
        print(row[0])
        print(row[1])
        nextBooking = booking.Booking(row[0],row[1])
        bookings.add(nextBooking)

    #print (bookings.size())

def read_db_details():
    conn = sqlite3.connect('./data/airline_seating.db')

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
            #print("in")
            freeSeats+=1

    #print("Number of rows is: ",nrows)
    #print("Seat lettering is: ", seats)
    #print ("Number of seats is: ", numberOfSeats)
    #print("Number of free seats is: ", freeSeats)

    resultsDict = {}
    resultsDict["nrows"]=nrows
    resultsDict["seatLettering"]=seats
    resultsDict["numberOfSeats"]=numberOfSeats
    resultsDict["freeSeats"]=freeSeats

    return resultsDict


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

    dbDetails = read_db_details()


    # read in the data
    #df = read_in_data()


    #for index, row in df.iterrows():
        # create a booking object with the name of the booker and the amount of seats required
        #a_booking = booking.Booking(row[0], row[1])

        # make the booking
        #make_booking(a_booking)


    #dbOperations.print_seating_plan()

main()

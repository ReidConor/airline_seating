import sqlite3
import pandas as pd
import numpy as np
import os
from model import booking, plane
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


#############
#Get all detais from the db and return. Some metrics returned may not be used
#############
def read_plane_details(pathToDB):
    #make a db connection
    conn = sqlite3.connect(pathToDB)

    #get db dimentions
    rows_and_columns = conn.cursor().execute("SELECT * FROM rows_cols;").fetchone()
    #list of rows numbers in the db, and the total number
    rows = np.arange(1,rows_and_columns[0]+1)
    nrows = len(rows)
    #seat lettering
    seats = rows_and_columns[1]
    numberOfSeats = nrows * len(seats)

    #get lists of free and occupied seats. Each record contains the row num, seat letter and name (if any)
    freeSeats = conn.cursor().execute("SELECT * FROM seating where name = '%s';" % '').fetchall()
    occupiedSeats = conn.cursor().execute("SELECT * FROM seating where name != '%s';" % '').fetchall()
    #sort the freeSeats list by row. Seats that are beside each other are now adjacent entries in this list
    freeSeats = sorted(freeSeats, key=lambda seat: freeSeats[0])#https://wiki.python.org/moin/HowTo/Sorting

    #create a dict of row numbers and the amount of seats available in each row, as well as what those seats actually are
    seatsInRows = {}
    for row in rows:
        seatsInRows[row] = [len(seats),str(seats)]

    #update to remove seats already taken at time of db read
    for seat in occupiedSeats:
        occupiedSeatLetter = seat[1]
        numSeatsLeftInRow = seatsInRows[seat[0]][0]
        seatsLeftInRow = seatsInRows[seat[0]][1]

        numSeatsLeftInRow -= 1
        seatsLeftInRow = seatsLeftInRow.replace(occupiedSeatLetter, "")#http://stackoverflow.com/questions/3559559/how-to-delete-a-character-from-a-string-using-python

    # print(seats_in_rows)

    #create a dict, fill it with this methods results
    planeDetails = {}
    planeDetails["rows"]=rows
    planeDetails["nrows"]=nrows
    planeDetails["seatLettering"]=seats
    planeDetails["numSeats"]=numberOfSeats
    planeDetails["numFreeSeats"]=len(freeSeats)
    planeDetails["numOccupiedSeats"]=len(occupiedSeats)
    planeDetails["listFreeSeats"]=freeSeats
    planeDetails["listOccupiedSeats"]=occupiedSeats
    planeDetails["seatsInRows"]=seatsInRows

    #close the sqlite db connection
    conn.close()

    #return the results
    return planeDetails


def make_booking(booking, planeDetails):
    conn = sqlite3.connect('./data/airline_seating.db')
    c = conn.cursor()



def main():

    #when runnign in terminal, clear the screen
    #os.system('cls')#for windows
    os.system('clear')#for linux based os

    #clean the db's exsiting entries
    # dbOperations.clean_db()

    # read in the data
    bookingsList = read_in_data("data/sample_bookings.csv")

    #read the plane details
    planeDetails = read_plane_details('data/airline_seating.db')
    print("rows: ",planeDetails["rows"])
    print("nrows: ",planeDetails["nrows"])
    print("seatLettering: ",planeDetails["seatLettering"])
    print("numSeats: ",planeDetails["numSeats"])
    print("numFreeSeats: ",planeDetails["numFreeSeats"])
    print("numOccupiedSeats: ",planeDetails["numOccupiedSeats"])
    print("listFreeSeats: ",planeDetails["listFreeSeats"])
    print("listOccupiedSeats: ",planeDetails["listOccupiedSeats"])
    print("seatsInRows: ",planeDetails["seatsInRows"])

    #make the booking for each entry
    # for booking in bookingsList:
        # make_booking(booking, planeDetails)

    #for index, row in df.iterrows():
        # create a booking object with the name of the booker and the amount of seats required
        #a_booking = booking.Booking(row[0], row[1])

        # make the booking
        #make_booking(a_booking)


    #dbOperations.print_seating_plan()

main()

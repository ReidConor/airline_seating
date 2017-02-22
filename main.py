import sqlite3
import pandas as pd
import numpy as np
import os
import sys
from model import booking
from db import dbOperations

def read_in_data(pathToFile):
    #catch an empty bookings file in a graceful way
    try:
        bookingsFile = pd.read_csv(pathToFile, sep=",", header=None)
    except pd.io.common.EmptyDataError:
        print("Bookings file is empty! Try another file..")
        bookingsFile = pd.DataFrame()
    except:
        raise

    allBookings = []
    for index, row in bookingsFile.iterrows():
        nextBooking = booking.Booking(row[0],row[1])
        allBookings.append(nextBooking)

    #below is a list of booking objects,
    #containing all bookings to be made
    return allBookings


#############
#Get all detais from the db and return. Some metrics returned may not be used in the end
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
    seats = (rows_and_columns[1])
    numberOfSeats = nrows * len(seats)

    #get lists of free and occupied seats. Each record contains the row num, seat letter and name (if any)
    freeSeats = conn.cursor().execute("SELECT * FROM seating where name = '%s';" % '').fetchall()
    occupiedSeats = conn.cursor().execute("SELECT * FROM seating where name != '%s';" % '').fetchall()
    #sort the freeSeats list by row. Seats that are beside each other are now adjacent entries in this list
    freeSeats = sorted(freeSeats, key=lambda seat: freeSeats[0])#https://wiki.python.org/moin/HowTo/Sorting

    #create a dict of row numbers and the amount of seats available in each row, as well as what those seats actually are
    seatsInRows = {}
    for row in rows:
        seatsInRows[row] = {}
        seatsInRows[row]["numSeats"]=len(seats)
        seatsInRows[row]["seatLetters"]=seats
    # print(seatsInRows)
    # print()

    #update to remove seats already taken at time of db read
    for seat in occupiedSeats:
        # print("Row number: ", seat[0])
        occupiedSeatLetter = seat[1]
        # print(occupiedSeatLetter)
        seatsInRows[seat[0]]["numSeats"] -= 1
        # print(seatsInRows[seat[0]]["seatLetters"])
        # seatsInRows[seat[0]]["seatLetters"].remove(str(occupiedSeatLetter))
        # seatsInRows[seat[0]]["seatLetters"] = seatsInRows[seat[0]]["seatLetters"].remove(str(occupiedSeatLetter))
        seatsInRows[seat[0]]["seatLetters"] = seatsInRows[seat[0]]["seatLetters"].replace(occupiedSeatLetter, '')#http://stackoverflow.com/questions/3559559/how-to-delete-a-character-from-a-string-using-python
    # print(seatsInRows)
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


def make_bookings(bookingsList, planeDetails, db):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    #set up metrics to be updated below
    passengersSeparated=0
    passengersRejected=0

    #loop through all incoming bookings
    for nextBooking in bookingsList:
        #get the maximum amount of seats in any one row, and find the last row where that is true
        maxInRow = 0
        rowNum = 0
        # print("There are: " , maxInRow, " seats in row number: ", rowNum)
        # print(rowNum)
        # for row in planeDetails["seatsInRows"].values():
        #     if maxInRow < row['numSeats']:
        #         maxInRow = row['numSeats']
        # print("Max seats in any row: ", maxInRow)
        for row in planeDetails["seatsInRows"]:
            # print()
            # print(planeDetails["seatsInRows"][row]['numSeats'])
            # print(row)
            # print(planeDetails["seatsInRows"][row]['numSeats'])
            # print(maxInRow)
            # print(nextBooking.parties)
            if planeDetails["seatsInRows"][row]['numSeats'] == nextBooking.parties:
                maxInRow = planeDetails["seatsInRows"][row]['numSeats']
                rowNum=row
                break
            elif planeDetails["seatsInRows"][row]['numSeats'] >= maxInRow:
                maxInRow = planeDetails["seatsInRows"][row]['numSeats']
                rowNum=row
                # print("There are: " , maxInRow, " seats in row number: ", rowNum)



        if planeDetails['numFreeSeats'] >= nextBooking.parties:
            #if this bookings parties is less than this max seat count
            if nextBooking.parties <= maxInRow:
                print("Can seat", nextBooking.name, "together for", nextBooking.parties, "people. Using row number: ", rowNum)
                row=planeDetails["seatsInRows"][rowNum]
                # print(row)s
                while nextBooking.parties > 0:
                    # print(nextBooking.name)
                    row['seatLetters'] = list(row['seatLetters'])
                    # print(row['seatLetters'])
                    seat = row['seatLetters'].pop()
                    # seatLetter = list(row['seatLetters']).pop()
                    # list(row['seatLetters']).remove('A')
                    # print(seatLetter)
                    # print("UPDATE seating SET name='%s' WHERE row=%d AND seat='%s';" %(nextBooking.name, rowNum, seat))
                    c.execute("UPDATE seating SET name='%s' WHERE row=%d AND seat='%s';" %(nextBooking.name, rowNum, seat))
                    # print(row['seatLetters'])
                    nextBooking.parties -= 1
                    planeDetails['numFreeSeats'] -= 1
                    row['numSeats'] -= 1
                    conn.commit()
            # elif nextBooking.parties <= planeDetails:
            else:
                print("Can't seat", nextBooking.name, "together for", nextBooking.parties, "people")
                #update metrics
                passengersSeparated += nextBooking.parties
                c.execute("UPDATE metrics SET passengers_separated='%s'" %passengersSeparated)

                passengerCounter = nextBooking.parties
                for row in planeDetails["seatsInRows"]:
                    if planeDetails["seatsInRows"][row]['numSeats'] > 0: #found a row that has some seats left
                        while(passengerCounter > 0):
                            while planeDetails["seatsInRows"][row]['numSeats'] > 0:
                                # print(planeDetails["seatsInRows"][row]['numSeats'])
                                # print(planeDetails["seatsInRows"][row]['seatLetters'])
                                planeDetails["seatsInRows"][row]['seatLetters'] = list(planeDetails["seatsInRows"][row]['seatLetters'])
                                thisSeat = planeDetails["seatsInRows"][row]['seatLetters'].pop()
                                # print(nextBooking.name, row, thisSeat)
                                c.execute("UPDATE seating SET name='%s' WHERE row=%d AND seat='%s';" %(nextBooking.name, row, thisSeat))
                                conn.commit()
                                passengerCounter-=1
                                planeDetails["seatsInRows"][row]['numSeats']-=1
                                planeDetails['numFreeSeats'] -= 1
                                if (passengerCounter == 0):
                                    break
                            break
        else:
            print("Cant do it for:", nextBooking.name, nextBooking.parties,  ". Not enough seats")
            passengersRejected+=1
            c.execute("UPDATE metrics SET passengers_refused='%s'" %passengersRejected)
            conn.commit()

def main(db, bookings):
    #when running in terminal, clear the screen
    #os.system('cls')#for windows
    os.system('clear')#for linux based os

    #clean the db's exsiting entries if required
    dbOperations.clean_db(db)

    # read in the data
    bookingsList = read_in_data(bookings)

    #read the plane details
    planeDetails = read_plane_details(db)
    # print("rows: ",planeDetails["rows"])
    # print("nrows: ",planeDetails["nrows"])
    # print("seatLettering: ",planeDetails["seatLettering"])
    # print("numSeats: ",planeDetails["numSeats"])
    # print("numFreeSeats: ",planeDetails["numFreeSeats"])
    # print("numOccupiedSeats: ",planeDetails["numOccupiedSeats"])
    # print("listFreeSeats: ",planeDetails["listFreeSeats"])
    # print("listOccupiedSeats: ",planeDetails["listOccupiedSeats"])
    # print("seatsInRows: ",planeDetails["seatsInRows"])

    #make the bookings
    make_bookings(bookingsList, planeDetails, db)

    #print the layout of the plane
    dbOperations.print_seating_plan(db)

if __name__ == "__main__":#http://stackoverflow.com/questions/6523791/why-is-python-running-my-module-when-i-import-it-and-how-do-i-stop-it

    #if args are three (ie file name itself, and the db and bookings file names)
    #use those
    #if not, use those stored in the project
    if len(sys.argv) == 3:
        db = sys.argv[1]
        bookings = sys.argv[2]
    else:
        print("No arguments provided. Using db and bookings files contained in the project.")
        db = "db/airline_seating.db"
        bookings = "data/bookings.csv"

    main(db, bookings)

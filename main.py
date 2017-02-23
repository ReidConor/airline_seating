import sqlite3
import pandas as pd
import numpy as np
import os
import sys
from model import booking
from db import dbOperations

def read_in_data(pathToFile):
    try: #catch an empty bookings file, and fail in a graceful manner
        bookingsFile = pd.read_csv(pathToFile, sep=",", header=None)
    except pd.io.common.EmptyDataError:
        print("Bookings file is empty! Try another file..")
        bookingsFile = pd.DataFrame()
    except:
        raise

    allBookings = []
    for index, row in bookingsFile.iterrows():
        nextBooking = booking.Booking(row[0],row[1]) #create a booking object for each booking in the csv
        allBookings.append(nextBooking)

    #below is a list of booking objects,
    #containing all bookings to be made
    return allBookings


#############
#Get all detais from the db and return in a dict.
#Some metrics returned here may not be used in the end.
#Idea is to return as much info as possible, and use whats needed
#############
def read_plane_details(pathToDB):
    conn = sqlite3.connect(pathToDB) #make a db connection
    c = conn.cursor()

    rows_and_columns = c.execute("SELECT * FROM rows_cols;").fetchone() #get db dimentions
    rows = np.arange(1,rows_and_columns[0]+1) #list of rows numbers in the db, and the total number
    nrows = len(rows) #get the number of rows
    seats = (rows_and_columns[1]) #get the seat lettering
    numberOfSeats = nrows * len(seats) #calculate the number of total seats in the plane

    freeSeats = c.execute("SELECT * FROM seating where name = '%s';" % '').fetchall() #get lists of free and occupied seats. Each record contains the row num, seat letter and name (if any)
    occupiedSeats = c.execute("SELECT * FROM seating where name != '%s';" % '').fetchall()

    #sort the freeSeats list by row. Seats that are beside each other are now adjacent entries in this list
    freeSeats = sorted(freeSeats, key=lambda seat: freeSeats[0])#https://wiki.python.org/moin/HowTo/Sorting

    seatsInRows = {} #create a dict of row numbers and the amount of seats available in each row, as well as what those seats actually are
    for row in rows:
        seatsInRows[row] = {}
        seatsInRows[row]["numSeats"]=len(seats)
        seatsInRows[row]["seatLetters"]=seats

    for seat in occupiedSeats: #update to remove seats already taken at time of db read
        occupiedSeatLetter = seat[1]
        seatsInRows[seat[0]]["numSeats"] -= 1
        #replace that seat with a blank
        seatsInRows[seat[0]]["seatLetters"] = seatsInRows[seat[0]]["seatLetters"].replace(occupiedSeatLetter, '')#http://stackoverflow.com/questions/3559559/how-to-delete-a-character-from-a-string-using-python

    planeDetails = {} #create a dict, fill it with this methods results
    planeDetails["rows"]=rows
    planeDetails["nrows"]=nrows
    planeDetails["seatLettering"]=seats
    planeDetails["numSeats"]=numberOfSeats
    planeDetails["numFreeSeats"]=len(freeSeats)
    planeDetails["numOccupiedSeats"]=len(occupiedSeats)
    planeDetails["listFreeSeats"]=freeSeats
    planeDetails["listOccupiedSeats"]=occupiedSeats
    planeDetails["seatsInRows"]=seatsInRows

    conn.close() #close the sqlite db connection

    return planeDetails #return the results dict


def make_bookings(bookingsList, planeDetails, db):
    conn = sqlite3.connect(db) #make a db connection
    c = conn.cursor()

    passengersTogether=0
    passengersSeparated=0#set up metrics to be updated in the db after bookings are made
    passengersRejected=0

    for nextBooking in bookingsList: #loop through all bookings in list
        #find a row with exactly the right number of free seats,
        #or stop when we find the last row in the plane where the
        #number of avaialable seats is greater than the booking
        maxInRow = 0
        rowNum = 0
        for row in planeDetails["seatsInRows"]:
            if planeDetails["seatsInRows"][row]['numSeats'] == nextBooking.parties:
                maxInRow = planeDetails["seatsInRows"][row]['numSeats']
                rowNum=row
                break
            elif planeDetails["seatsInRows"][row]['numSeats'] >= maxInRow:
                maxInRow = planeDetails["seatsInRows"][row]['numSeats']
                rowNum=row


        if planeDetails['numFreeSeats'] >= nextBooking.parties: #check if the number of free seats is greater or equal to the booking size
            if nextBooking.parties <= maxInRow: #if this bookings parties is less than or equal to the maximum free seats together, we can accomadate the booking together (not split up)
                passengersTogether+=nextBooking.parties
                #print("Can seat", nextBooking.name, "together for", nextBooking.parties, "people.")
                row=planeDetails["seatsInRows"][rowNum] #get the free seats from the row that was chosen as best above
                passengerCounter = nextBooking.parties #setup a counter for passengers left to book
                while passengerCounter > 0: #cycle through the size of the bookings
                    row['seatLetters'] = list(row['seatLetters']) #split the free seats string into its components...ie from 'ABC' to 'A','B','C'
                    seat = row['seatLetters'].pop() #pop the last seat in the list...ie return it and remove it from the free seats list
                    c.execute("UPDATE seating SET name='%s' WHERE row=%d AND seat='%s';" %(nextBooking.name, rowNum, seat)) #make the booking in the db
                    passengerCounter -= 1 #decrement the amount of parties left to book
                    planeDetails['numFreeSeats'] -= 1 #decrement free seat count
                    row['numSeats'] -= 1 #decrement free seat count in this particular row
                    conn.commit() #commit changes made so far

            else: #if booking size is greater than the max seats together, we have to split the group up
                #print("Can not seat", nextBooking.name, "together for", nextBooking.parties, "people.")
                passengersSeparated += nextBooking.parties #update separated passengers
                passengerCounter = nextBooking.parties #setup a counter for passengers left to book
                for row in planeDetails["seatsInRows"]: #cycle through plane rows
                    if planeDetails["seatsInRows"][row]['numSeats'] > 0: #found a row that has some seats left
                        while(passengerCounter > 0): #while there is still people to book
                            while planeDetails["seatsInRows"][row]['numSeats'] > 0: #while there are seats left to book them in
                                planeDetails["seatsInRows"][row]['seatLetters'] = list(planeDetails["seatsInRows"][row]['seatLetters']) #split the free seats string into its components...ie from 'ABC' to 'A','B','C'
                                thisSeat = planeDetails["seatsInRows"][row]['seatLetters'].pop() #pop a seat to use for the current booking
                                c.execute("UPDATE seating SET name='%s' WHERE row=%d AND seat='%s';" %(nextBooking.name, row, thisSeat)) #make the booking in the db
                                conn.commit() #commit the above change
                                passengerCounter-=1 #decrement the amount of parties left to book
                                planeDetails["seatsInRows"][row]['numSeats']-=1 #decrement free seat count
                                planeDetails['numFreeSeats'] -= 1 #decrement free seat count in this particular row
                                if (passengerCounter == 0): #if there are no more passengers to book seats for
                                    break #break out
                            break
        else: #there arent enough seats left to accomadate this booking
            #print("Can not seat", nextBooking.name, "for", nextBooking.parties, "people. Not enough seats.")
            passengersRejected+=1 #increment the amount of rejected passengers

    print() #print out a summary of the booking process
    print("Summary")
    print("-------")
    print("Passengers seated together:", passengersTogether )
    print("Passengers seated, but not together:", passengersSeparated )
    print("Passengers refused:", passengersRejected)

    c.execute("UPDATE metrics SET passengers_separated='%s'" %passengersSeparated) #move to outside the for loop. prevents needless db writes
    c.execute("UPDATE metrics SET passengers_refused='%s'" %passengersRejected) #move to outside the for loop. prevents needless db writes
    conn.commit() #commit the changes


#main function that calls the above
def main(db, bookings):

    dbOperations.clean_db(db)#clean the db's exsiting entries if required, commented out for submission perposes, used a lot during development

    bookingsList = read_in_data(bookings) #read in the data

    planeDetails = read_plane_details(db) #read the plane details

    make_bookings(bookingsList, planeDetails, db) #make the bookings

    dbOperations.print_seating_plan(db) #print the layout of the plane after bookings are made to the console



if __name__ == "__main__":#http://stackoverflow.com/questions/6523791/why-is-python-running-my-module-when-i-import-it-and-how-do-i-stop-it
    #when running in terminal, clear the screen
    #os.system('cls')#for windows
    #os.system('clear')#for linux based os

    if len(sys.argv) == 3: #if args are three (ie file name itself, and the db and bookings file names), use those
        db = sys.argv[1]
        bookings = sys.argv[2]
    else: #if not, use those stored in the project
        print("No arguments provided. Using db and bookings files contained in the project.")
        db = "db/airline_seating.db"
        bookings = "data/bookings.csv"

    main(db, bookings) #call the main with arguments

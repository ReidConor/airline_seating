import unittest
import os
import pandas as pd
import numpy as np
from types import *
import sys
import sqlite3
import main
from db import dbOperations
#from https://docs.python.org/2/library/unittest.html
class airlineReservationSystemTests(unittest.TestCase):
    #give the read_in_data function an empty booking file and test output
    #tests if this method fails gracefully
    def test_read_in_data_empty(self):
        #using a tip from the below link to silence output
        #http://stackoverflow.com/questions/2828953/silence-the-stdout-of-a-function-in-python-without-trashing-sys-stdout-and-resto
        old_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")
        try:
            emptyList = main.read_in_data("test/data/bookings_empty.csv")
        finally:
            sys.stdout.close()
            sys.stdout = old_stdout
        self.assertEqual(0, len(emptyList))

    #give a booking file containing one record
    #tests if the resulting list is of the correct size
    def test_read_in_data_nonEmpty(self):
        oneRecordList = main.read_in_data("test/data/bookings_oneRecord.csv")
        self.assertEqual(1, len(oneRecordList))
        allRecordsList = main.read_in_data("test/data/bookings.csv")
        self.assertEqual(100, len(allRecordsList))


    #give read_plane_details function the stock db and test resulting dict's attribute types
    def test_read_plane_details_types(self):
        stockPlaneDetails = main.read_plane_details("test/db/airline_seating.db")
        assert type(stockPlaneDetails["nrows"]) is int
        assert type(stockPlaneDetails["rows"]) is np.ndarray
        assert type(stockPlaneDetails["seatLettering"]) is str
        assert type(stockPlaneDetails["numSeats"]) is int
        assert type(stockPlaneDetails["numFreeSeats"]) is int
        assert type(stockPlaneDetails["numOccupiedSeats"]) is int
        assert type(stockPlaneDetails["listFreeSeats"]) is list
        assert type(stockPlaneDetails["listOccupiedSeats"]) is list
        assert type(stockPlaneDetails["seatsInRows"]) is dict

    #give the read_plane_details function two different db's and test the resulting dict's content
    def test_read_plane_details_content(self):
        #if the stock db is ever written to, these test will fail
        stockPlaneDetails = main.read_plane_details("test/db/airline_seating_stock.db")
        self.assertEqual((stockPlaneDetails["nrows"]),15)
        self.assertEqual((stockPlaneDetails["seatLettering"]),"ACDF")
        self.assertEqual((stockPlaneDetails["numSeats"]),60)
        self.assertEqual(len(stockPlaneDetails["listFreeSeats"]),58)

        #clean the altered db, since it is used in a following test that inserts bookings
        dbOperations.clean_db("test/db/airline_seating_altered.db")
        alteredPlaneDetails = main.read_plane_details("test/db/airline_seating_altered.db")
        self.assertEqual((alteredPlaneDetails["nrows"]),16)
        self.assertEqual((alteredPlaneDetails["seatLettering"]),"wXYZ")
        self.assertEqual((alteredPlaneDetails["numSeats"]),64)
        self.assertEqual(len(alteredPlaneDetails["listFreeSeats"]),64)

    #perform some limited testing on the main method
    def test_main(self):
        #same altered db as above
        db = "test/db/airline_seating_altered.db"
        bookings = "test/data/bookings.csv"

        #using a tip from the below link to silence output
        #http://stackoverflow.com/questions/2828953/silence-the-stdout-of-a-function-in-python-without-trashing-sys-stdout-and-resto
        old_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")
        try:
            main.main(db, bookings)
        finally:
            sys.stdout.close()
            sys.stdout = old_stdout

        #we know for sure that the bookings.csv contains bookings for more than the seats in this db
        #test to see if there are any free seats, ie if the program hasnt filled all seats
        conn = sqlite3.connect(db)
        c = conn.cursor()
        freeSeats = conn.cursor().execute("SELECT * FROM seating where name = '%s';" % '').fetchall()
        self.assertEqual(len(freeSeats),0)
        #TODO: put in test for poeple sitting apart etc??



if __name__ == '__main__':
    os.system('clear')#for linux based os
    unittest.main()

# Airline Seating Assignment

This repositiory contains python code written as fulfilment of the second programming assignment for MIS40750 (Analytics Research &amp; Implementation)

## Getting Started

This is a short note on how to get this project setup in your local environment, and tools that will aid further development and running.

### Prerequisites

This program has been developed and tested using Python 3.5.2. Thus it is highly recommend to use Python 3.X.X when developing and running further. 

The version of Sqlite3 used during development is 3.13.0. Again, using a similar version for future development and running is likely to prevent error. 

### Tools

Listed here are the tools that were used during development of the Airline Seating program. 

- [Atom](https://atom.io)
- [db visualizer for sqlite3](http://www.dbvis.com/doc/sqlite-database-support/)
- Terminal
- Excel

## Running Airline Seating
Run the main file with

```
    python seat_assign_10345681.py
```
The above command runs the program with the stock db and bookings file provided in the asignment brief. To run the program aganist an alternative database or list of bookings, use:
```
    python seat_assign_10345681.py <path_to_db> <path_to_bookings>
```

Some sumary details are printed to the console for priliminary inspection including;
- The number of passengers sitting together
- The number sitting apart
- The number of refused passengers. 

## Running the tests

Some unit and integration tests are included in this project. To run these use:
```
    python seat_assign_10345681_test.py
```

The amount of tests that pass and fail with be printed to the console. 

## Program Steps

A .csv file containing bookings is read line by line (```read_in_data```), each record stored in a "booking" object and appended to a list. This list is returned to be used in the main function.

Next, the database is queried and details extracted (```read_plane_details```). Details include the dimensions of the plane, the number of pre-existing bookings and the number of free seats available. These details are stored in a dictionary, and returned. A dictionary is returned here for clarity of use and easy value look-up later on. 

The main function in the program (```make_bookings```) calls the two functions above. It then begins to allocate bookings (on a first come first serve basis) to the remaining seats in the database. To do this, it first checks if any row has exactly enough seats to accommodate the next booking. If so, this row is chosen. If not, a row with more than enough seats is chosen and the booking is fulfilled. When this happens, the booking is considered to be non-separated. When no row has enough seats on its own to accommodate the next booking, but the overall number of free seats is greater than the booking size, we consider the booking separated since parties sit in non-adjacent seats. A record of these cases is kept, and written to the database.

Once the amount of free seats in the database reaches zero, all subsequent bookings are rejected. A count of these is kept, and written to the database metrics table before the application terminates. 

For more technical and detailed documentation, see comments in the [seat_assign_10345681.py](https://github.com/ReidConor/airline_seating/blob/master/seat_assign_10345681.py) file.


## Author

* **Conor Reid** 
    *C10345681* 
    conor.reid@ucdconnect.ie

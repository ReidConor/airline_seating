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

A .csv file containing bookings is read line by line, each stored in a "booking" object and appended to a list. This list is returned.

Next, the database is queried and details extracted. Details include the dimentions of the plane, the number of pre-exisitng bookings and the number of free seats available. These details are stored in a dictionary, and returned. 

The main body of the program calls the two functions above. It then begins to allocate bookings (on a first come first serve basis) to the remaining seats in the database. To do this, it first checks if any row has enough free seats on its own to accomadate the next booking. If so, that row is chosen and the booking is fulfilled. When this happens, the booking is considered to be non-separated. When no row has enough seats on its own to accomadate a booking, but the overall number of free seats is greater than the booking size, we consider the booking separated since parties sit in non-ajacent seats. 

1. Read in Bookings
    A .csv file containing bookings is read line by line, stored in a "booking" object and appended to a list. This list is returned. 

2. Read the Database Details
    Here is step two
3. Make the Bookings
    Here is step three
4. Print Summary
    Here is step four

## Author

* **Conor Reid** 
    *C10345681* 
    conor.reid@ucdconnect.ie

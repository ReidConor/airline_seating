import sys

class Booking:
    def __init__(self, name, parties):
        self.name = name
        self.parties = parties

    def __str__(self):
        return self.name + " " + str(self.parties)

import sys


class Booking:
    def __init__(self, name, parties):
        self.name = name
        self.parties = parties
        self.accepted = False
        self.sittingTogether = False

    def __str__(self):
        return self.name + " " + self.parties

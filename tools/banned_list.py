# GMG Copyright 2022 - Alexandre Díaz
import re
import time


class BannedList(object):
    def __init__(self):
        self.banlist = []

    def add(self, address, time):
        if address in self.banlist:
            raise Exception('Address already banned')
        self.banlist.append(BanLine(address, time))

    def find(self, address=None):
        output = []
        if address:
            address = re.compile(address, re.IGNORECASE)
        for line in self.banlist:
            if address == None or address.search(line.address):
                output.append(line)
        return output

    def refresh(self):
        for line in self.banlist:
            if time.time() >= line.end:
                self.banlist.remove(line)

    def sort(self, cmp=None, key=None, reverse=False):
        self.banlist = sorted(self.banlist, cmp, key, reverse)

    def reverse(self):
        self.banlist.reverse()

    def clear(self):
        del self.banlist[:]

    def __len__(self):
        return len(self.banlist)

    def __iter__(self):
        return iter(self.banlist)

    def __repr__(self):
        return str(self.banlist)


class BanLine(object):
    def __init__(self, address, time_ban):
        self.address = address
        self.end = time.time() + time_ban

    def __repr__(self):
        return "<Ban ip='{0}' end='{1}'>".format(self.address, self.end)

    def __contains__(self, item):
        return True if self.address is item else False

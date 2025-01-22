import os

class MatchingContentNotFound(Exception):
    pass

class NoFillerContentFound(Exception):
    pass

class CatalogEntry:
    def __init__(self, path, duration, tag, hints=[]):
        self.path = path
        #get the show name from the path
        self.title = os.path.basename(path).split(".")[0]
        self.duration = duration
        self.tag = tag
        self.count = 0
        self.hints = hints

    def __str__(self):
        hints = list(map(str, self.hints))
        return f"{self.title:<20.20} | {self.tag:<10.10} | {self.duration:<8.1f} | {hints}"
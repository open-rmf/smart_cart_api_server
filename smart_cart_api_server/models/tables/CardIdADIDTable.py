from typing import List

class UserInfo:
    def __init__(self, adid: str, waypoints: List[str]):
        self.adid = adid
        self.waypoints = waypoints


class AbstractCardIdADIDTable:
    def lookup_cardid(self, card_id: str) -> UserInfo|None:
        return None

class InMemoryCardIdADIDTable(AbstractCardIdADIDTable):
    def __init__(self) -> None:
        self.table = {"card_0": UserInfo("admin", ["clinic"])}

    def lookup_cardid(self, card_id: str) -> UserInfo|None:
        if not card_id in self.table:
            return None
        return self.table[card_id]

import csv
class CSVCardIdADIDTable(AbstractCardIdADIDTable):
    def __init__(self, filename: str) -> None:
        self.table = {}
        with open(filename) as csvfile:
            spamreader = csv.reader(csvfile)
            for row in spamreader:
                if len(row) < 2:
                    raise "CSV file is misformatted. File format should be \"CARDID\", \"ADID\" and locations"
                self.table[row[0]] = UserInfo(row[1], row[2:])

    def lookup_cardid(self, card_id: str) -> UserInfo|None:
        if not card_id in self.table:
            return None
        return self.table[card_id]

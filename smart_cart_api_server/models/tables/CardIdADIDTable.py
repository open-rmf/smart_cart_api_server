from typing import List

class UserInfo:
    def __init__(adid: str, waypoints: List[str]):
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


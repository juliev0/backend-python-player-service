import sqlite3
from datetime import date

from app_paths import PLAYER_DB


class PlayerService:
    def __init__(self):
        conn = sqlite3.connect(PLAYER_DB)
        self.conn = conn
        self.cursor = conn.cursor()
        self.columns = self.get_columns()

    def get_all_players(self):

        query = "SELECT * FROM players"
        result = self.cursor.execute(query).fetchall()
        players = []
        for row in result:
            dic = self.convert_row_to_dict(row)
            players.append(dic)

        return players

    def search_by_player(self, player_id):

        query = "SELECT * FROM players WHERE playerId='{}'".format(player_id)
        result = self.cursor.execute(query).fetchall()

        for row in result:
            dic = self.convert_row_to_dict(row)
        return dic

    def search_by_country(self, birth_country):

        query = "SELECT * FROM players WHERE birthCountry='{}'".format(birth_country)
        result = self.cursor.execute(query).fetchall()

        return result

    def convert_row_to_dict(self, row):
        dic = {self.columns[i]: row[i] for i in range(len(row))}
        dic["age"] = self.calculate_age(dic)
        return dic

    @staticmethod
    def calculate_age(player, today=None):
        """Returns the player's age in whole years, or None if the birth year is unknown.

        For players who have died, the age is measured at the date of death.
        Otherwise it is measured as of `today` (defaults to the current date).
        Missing birth/death months or days are treated as the 1st of the month/year.
        """
        birth_year = PlayerService._to_int(player.get("birthYear"))
        if birth_year is None:
            return None

        birth_month = PlayerService._to_int(player.get("birthMonth")) or 1
        birth_day = PlayerService._to_int(player.get("birthDay")) or 1

        # Choose the reference date: date of death if known, otherwise today.
        death_year = PlayerService._to_int(player.get("deathYear"))
        if death_year is not None:
            death_month = PlayerService._to_int(player.get("deathMonth")) or 1
            death_day = PlayerService._to_int(player.get("deathDay")) or 1
            reference = (death_year, death_month, death_day)
        else:
            today = today or date.today()
            reference = (today.year, today.month, today.day)

        # Subtract a year if the birthday has not yet occurred in the reference year.
        age = reference[0] - birth_year
        if (reference[1], reference[2]) < (birth_month, birth_day):
            age -= 1
        return age

    @staticmethod
    def _to_int(value):
        """Converts a database value (which may be None, NaN, or a float) to an int, or None."""
        if value is None or value == "" or value != value:
            return None
        return int(value)

    def get_columns(self):
        self.cursor.execute("PRAGMA table_info(players)")
        columns = [column[1] for column in self.cursor.fetchall()]
        return columns

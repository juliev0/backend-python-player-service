from datetime import date

import pytest

from player_service import PlayerService

TODAY = date(2026, 11, 3)


def test_age_after_birthday_this_year():
    player = {"birthYear": 1981, "birthMonth": 10, "birthDay": 1}
    assert PlayerService.calculate_age(player, today=TODAY) == 45


def test_age_before_birthday_this_year():
    player = {"birthYear": 1981, "birthMonth": 12, "birthDay": 27}
    assert PlayerService.calculate_age(player, today=TODAY) == 44


def test_age_on_birthday():
    player = {"birthYear": 2000, "birthMonth": 11, "birthDay": 3}
    assert PlayerService.calculate_age(player, today=TODAY) == 26


def test_age_for_deceased_player_is_age_at_death():
    player = {
        "birthYear": 1939, "birthMonth": 8, "birthDay": 5,
        "deathYear": 1984, "deathMonth": 8, "deathDay": 16,
    }
    assert PlayerService.calculate_age(player, today=TODAY) == 45


def test_age_is_none_when_birth_year_missing():
    assert PlayerService.calculate_age({"birthYear": None}, today=TODAY) is None
    assert PlayerService.calculate_age({"birthYear": float("nan")}, today=TODAY) is None


def test_age_handles_missing_month_and_day_and_float_values():
    player = {"birthYear": 1990.0, "birthMonth": None, "birthDay": float("nan")}
    assert PlayerService.calculate_age(player, today=TODAY) == 36


def test_get_players_includes_age(client):
    players = client.get("/v1/players").get_json()
    assert all("age" in player for player in players)


def test_get_player_by_id_includes_age(client):
    response = client.get("/v1/players/aaronha01")
    assert response.status_code == 200
    body = response.get_json()
    assert body["playerId"] == "aaronha01"
    # Hank Aaron (born 1934-02-05) is alive in the dataset, so age depends on today's date.
    expected_age = PlayerService.calculate_age(body)
    assert body["age"] == expected_age
    assert isinstance(body["age"], int)


def test_get_deceased_player_by_id_returns_age_at_death(client):
    body = client.get("/v1/players/aaronto01").get_json()
    assert body["age"] == 45


@pytest.fixture
def client():
    from app import app

    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client

from rich import print

from egse.storage.persistence import SQLite
from egse.system import format_datetime


def test_creation_of_database():

    # The enforced extension for the database file is 'sqlite3'

    db = SQLite('xxx.db')
    assert str(db.get_filepath()) == 'xxx.sqlite3'

    # Creating the SQLite object should not yet create the database file

    assert not db.get_filepath().exists()

    db.open()  # this will create the file
    db.close()

    assert db.get_filepath().exists()

    db.get_filepath().unlink()


def test_create_table():

    db = SQLite('obsid-table')

    db.open()
    columns = {
        'test_id': "integer primary key",
        'site_id': "text not null",
        'setup_id': "integer not null",
        'timestamp': "text not null",
        'function': "text",
        'description': "text",
    }
    db.create_table("observations", columns=columns)

    data = {
        'test_id': 1,
        'site_id': "CSL",
        'setup_id': 63,
        'timestamp': format_datetime(),
        'function': "rotation_stage_move(angle='10')"
    }
    db.add_to_table("observations", data)

    data = {
        'test_id': 2,
        'site_id': "CSL",
        'setup_id': 63,
        'timestamp': format_datetime(),
        'function': "rotation_stage_move(angle=\"12\")"
    }
    db.add_to_table("observations", data)

    criteria = {

    }
    cur = db.select_from_table("observations", criteria=criteria)
    result = cur.fetchall()

    assert len(result) == 2
    assert "angle='10'" in result[0][4]
    assert 'angle="12"' in result[1][4]

    db.get_filepath().unlink()

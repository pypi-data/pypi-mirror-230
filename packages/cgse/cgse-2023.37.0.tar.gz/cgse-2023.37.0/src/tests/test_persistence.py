from pathlib import Path

import pytest

from egse.storage.persistence import CSV1
from egse.storage.persistence import CSV2
from egse.storage.persistence import HDF5
from egse.storage.persistence import TXT
from egse.storage.persistence import parts


def test_txt_not_opened():

    with pytest.raises(OSError):
        txt = TXT('xxx.txt')
        txt.create('This is the first line in the TXT file')
        txt.close()


def test_txt_normal_use():

    txt = TXT('xxx.txt', prep={'ending': '\n', 'mode': 'w'})
    txt.open()
    txt.create('This is the first line in the TXT file.')
    txt.create('')  # is this an empty line?
    txt.create({'key 1': 'a string', 'key 2': 42})
    txt.create('Last line in the file.')
    txt.close()

    check_file('xxx.txt', {1: '\n', 2: "{'key 1': 'a string', 'key 2': 42}\n"})

    Path("xxx.txt").unlink()


def test_txt_with_statement():

    with TXT('yyy.txt').open(mode='w') as txt:
        txt.create("\nSecond line.\n")

    check_file('yyy.txt', {1: 'Second line.\n'})

    Path('yyy.txt').unlink()


def test_txt_read():

    filename = 'zzz.txt'
    with TXT(filename, prep={"mode": 'w'}) as txt:
        for n in range(20):
            txt.create(f"{n}\t{n**2}\n")

    txt = TXT(filename).open()
    assert len(list(txt.read())) == 20
    txt.close()

    with TXT(filename) as txt:
        for line in txt.read():
            if line.startswith('15'):
                assert line.split()[1] == 225  # just to check something...


# TODO:
#   find out how to run the test for CSV1 and CSV2 automatically


@pytest.mark.parametrize("CSV", [CSV1, CSV2])
def test_csv_with_statement(CSV):

    filenames = ["aaa.csv", "bbb.csv", "ccc.csv", "ddd.csv"]

    cleanup_files(filenames)

    files = iter(filenames)

    # ----------------------------------------------------------------------

    filename = next(files)

    with CSV(filename, prep={'mode': 'w'}) as csv:
        csv.create("# This file was generated from the test_csv_with_statement unit test.")
        csv.create([4, 5, 6])
        # this line will not be written, as there was no column_names provided
        csv.create({'a': 65, 'b': 66, 'c': 67})

    assert not csv.is_open()

    csv = CSV(filename).open()
    assert len(list(csv.read())) == 2
    csv.close()

    check_file(filename, {1: "4,5,6\n"})

    # ----------------------------------------------------------------------

    filename = next(files)

    with CSV(filename, prep={'column_names': ['a', 'b', 'c'], 'mode': 'w'}) as csv:
        csv.create({'a': 1, 'c': 3, 'b': 2})

    check_file(filename, {1: "1,2,3\n"})

    # ----------------------------------------------------------------------

    filename = next(files)

    f = CSV(filename, prep={'column_names': ["col 1", "col 2"], 'mode': 'w'})
    f.open()
    f.create("# Just one line in the file")
    f.create({'col 1': 1, 'col 2': 2})

    with CSV(filename).open(mode='r') as csv:
        for line in csv.read():
            print(" | ".join(line))

    assert csv.is_open()
    csv.close()

    f.create("# Second line in the file")
    f.close()

    csv = CSV(filename).open(mode='a')
    assert csv.is_open()
    csv.create("# append a string to the csv file.")
    csv.close()

    check_file(filename, {
        0: "col 1,col 2\n",
        2: "1,2\n",
        4: "# append a string to the csv file.\n",
    })

    # ----------------------------------------------------------------------

    filename = next(files)

    csv = CSV(filename, prep={'column_names': ['one', 'two', 'three']})

    with csv.open(mode='w') as csv:
        for i in range(10):
            csv.create([i, i**2, i**3])

    assert csv.is_open()

    csv.update(2, [3, 4, 5])  # not implemented

    csv.close()

    assert not csv.is_open()

    check_file(filename, {0: "one,two,three\n", 8: "7,49,343\n"})

    cleanup_files(filenames)


@pytest.mark.parametrize("quote_char", ['|', '"', "'"])
@pytest.mark.parametrize("delimiter", [",", ":"])
@pytest.mark.parametrize("CSV", [CSV1, CSV2])
def test_csv_quote_char(quote_char, delimiter, CSV):
    # Test the introduction of the quote_char keyword argument for CSV1 and CSV2

    filename = "test-file.csv"

    # Default quote_char = '"'

    prep = {
        'column_names': ["A float", "A string", "A string with commas", "A list"],
        'quote_char': quote_char, 'delimiter': delimiter, 'mode': 'w'
    }
    with CSV(filename, prep=prep) as csv:
        csv.create([3.14, "7.26", "1, 2, 3, 4", [5, 6, 7, 8]])

    # The check_file function checks the content as plain ascii text,
    # so this is was the actual file content looks like

    if delimiter == ",":
        check_file(filename, {
            1: f"3.14{delimiter}7.26{delimiter}{quote_char}1, 2, 3, 4{quote_char}{delimiter}{quote_char}[5, 6, 7, 8]{quote_char}\n"
        })
    else:
        check_file(filename, {
            1: f"3.14{delimiter}7.26{delimiter}1, 2, 3, 4{delimiter}[5, 6, 7, 8]\n"
        })

    # The check_csv_file checks the file as a CSV file,
    # so this is what is read back from the CSV file

    check_csv_file(CSV, filename, {1: ['3.14', '7.26', '1, 2, 3, 4', '[5, 6, 7, 8]']}, delimiter, quote_char)

    cleanup_files([filename])


@pytest.mark.skip
def test_read_last_group_hdf5():
    location = Path("/Users/rik/data/CSL/daily")
    filename = "20210521_CSL_N-FEE_SPW.hdf5"

    with HDF5(filename=location / filename, prep={"mode": 'r'}) as hdf5:
        rc = hdf5.read(select="last_top_group")
        print(f"{rc=}")
        assert rc == -1


def cleanup_files(filenames):
    for filename in filenames:
        try:
            Path(filename).unlink()
        except FileNotFoundError:
            pass


def check_file(filename, lines):
    # Read the file as a normal text file, also for CSV format, just read and
    # compare the complete line

    print("\ncheck_file:")

    with open(filename) as fd:
        for lineno, line in enumerate(fd):
            line_check = lines.get(lineno)
            if line_check:
                print(f"{line_check.rstrip()} == {line.rstrip()}")
                assert line_check == line


def check_csv_file(CSV, filename, lines, delimiter, quote_char):
    print("\ncheck_csv_file:")

    with CSV(filename, prep={'delimiter': delimiter, 'quote_char': quote_char, 'mode': 'r'}) as csv:
        reader = csv.read()
        for lineno, line in enumerate(reader):
            line_check = lines.get(lineno)
            if line_check:
                print(f"{line_check} == {line}")
                print(f"{type(line_check)=} == {type(line)=}")
                [print(f"{type(a)=} == {type(b)=}") for a, b in zip(line_check, line)]
                assert line == line_check
                assert all(a == b for a, b in zip(line_check, line))


@pytest.mark.parametrize("quote_char", ['|', '"', "'"])
@pytest.mark.parametrize("delimiter", [",", ":"])
def test_parts(delimiter, quote_char):

    data = f"3.14{delimiter}7.26{delimiter}{quote_char}1, 2, 3, 4{quote_char}{delimiter}{quote_char}[5, 6, 7, 8]{quote_char}"
    actual = parts(data, delimiter, quote_char)
    expected = ['3.14', '7.26', '1, 2, 3, 4', '[5, 6, 7, 8]']

    print()
    print(f"{data    =}")
    print(f"{actual  =}")
    print(f"{expected=}")

    assert actual == expected

    data = 'par1=val1,par2=val2,par3="some text1, again some text2, again some text3",par4="some text",par5=val5'
    actual = parts(data, keep_quote_char=True)
    expected = ['par1=val1', 'par2=val2', 'par3="some text1, again some text2, again some text3"', 'par4="some text"', 'par5=val5']

    print()
    print(f"{data    =}")
    print(f"{actual  =}")
    print(f"{expected=}")

    assert actual == expected

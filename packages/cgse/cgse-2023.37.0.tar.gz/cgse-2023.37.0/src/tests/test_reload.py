import sys
import textwrap
from pathlib import Path

from egse.reload import reload_function
from egse.reload import reload_module

FILE_LOCATION = Path(__file__).parent


def test_reload_module_and_function():

    A = FILE_LOCATION / "A.py"
    B = FILE_LOCATION / "B.py"

    print()

    with A.open('w') as fd:
        fd.write(
            textwrap.dedent(
                """
                def func_a():
                    print("inside the old func_a()")
                    return 2
                """
            )
        )

    reload_module('A')
    from A import func_a
    assert func_a() == 2  # prints 'inside the old func_a()'

    # Now make some changes in func_a()

    with A.open('w') as fd:
        fd.write(
            textwrap.dedent(
                """
                def func_a():
                    print("inside the new func_a()")
                    return 4
                """
            )
        )

    func_a = reload_function(func_a)
    assert func_a() == 4  # prints 'inside the new func_a()

    # Now create a func_b() which calls func_a and then make a change in func_a() again
    # This will test the dependency loading, i.e. when func_b() calls func_a() the module
    # where this last function resides needs to be reloaded.

    with B.open('w') as fd:
        fd.write(
            textwrap.dedent(
                """
                from A import func_a 
                def func_b():
                    print("inside func_b(), calling func_a()")
                    return func_a()
                """
            )
        )

    from B import func_b
    assert func_b() == 4  # prints 'inside func_b(), calling func_a()'
                          #        'inside the new func_a()'

    # Make again some changes in func_a

    # Now make some changes in func_a()

    with A.open('w') as fd:
        fd.write(
            textwrap.dedent(
                """
                def func_a():
                    print("inside the newest func_a()")
                    return 6
                """
            )
        )

    reload_module('A')
    reload_function(func_b)
    from B import func_b

    assert func_b() == 6  # prints 'inside func_b(), calling func_a()'
                          #        'inside the newest func_a()'

    # cleanup

    A.unlink()
    B.unlink()

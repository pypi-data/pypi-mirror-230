# test_manwrapper.py

from manwrapper.main import get_man_page

def test_get_man_page():
    # Test a known command
    result = get_man_page('ls')
    assert "list directory contents" in result

    # Test an unknown command
    result = get_man_page('nonexistentcommand')
    assert "Error:" in result

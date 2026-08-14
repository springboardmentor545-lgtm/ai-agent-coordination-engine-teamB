from tools.calculator import calculate

def test_addition():
    assert calculate("10 + 5") == 15

def test_precedence():
    assert calculate("2 + 3 * 4") == 14

def test_setup(test):
    assert test is None


def test_version():
    import pgfutil
    assert pgfutil.__version__ == '0.0.2'

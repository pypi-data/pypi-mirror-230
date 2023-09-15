def test_version(mocker):
    mocker.patch("gitmojis.__version__", "__version__")

    from gitmojis import __version__

    assert __version__ == "__version__"

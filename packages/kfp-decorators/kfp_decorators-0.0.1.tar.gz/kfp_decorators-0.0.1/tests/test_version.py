from kfp_decorators import __version__


def test_version() -> None:
    """Test that the version number is set correctly."""
    assert __version__

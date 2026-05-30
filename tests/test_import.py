"""Test that the game module can be imported without errors."""


def test_game_module_imports(gm):
    """Sanity check: conftest successfully imported the game module."""
    assert gm is not None
    assert hasattr(gm, 'BattleManager')
    assert hasattr(gm, 'Card')
    assert hasattr(gm, 'CARD_DATABASE')
    assert hasattr(gm, 'CARD_NAME_TO_KEY')
    assert hasattr(gm, 'AnimationManager')
    assert hasattr(gm, 'SoundManager')
    assert hasattr(gm, 'Particle')
    assert hasattr(gm, 'save_game')
    assert hasattr(gm, 'load_game')

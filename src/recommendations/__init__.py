"""Uses Sim's real engine (src/recommendations/engine.py) when it exists, else the mock."""
try:
    from .engine import recommend_rotations  # noqa: F401
    IS_MOCK = False
except ImportError:
    from .mock_engine import recommend_rotations  # noqa: F401
    IS_MOCK = True

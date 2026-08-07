"""Test package marker.

Present so that `conftest.py` files in sibling directories resolve to distinct
module paths. Without it, mypy reports a duplicate module named "conftest".
"""

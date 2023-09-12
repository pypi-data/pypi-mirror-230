import pytest

from substring_structures import KMPPrefixFallbackStructure


@pytest.mark.parametrize(
    "substring,superstring,substring_in_superstring",
    [
        ("a", "abab", True),
        ("b", "abab", True),
        ("ba", "abab", True),
        ("abab", "abab", True),
        ("bab", "abab", True),
        ("aba", "abab", True),
        ("babababababad", "ababababababababababababadababa", True),
        ("", "abab", True),
        ("", "", True),
        ("ababa", "abab", False),
        ("bad", "abab", False),
        ("bababab", "babadababa", False),
    ],
)
def test_contained_by(substring: str, superstring: str, substring_in_superstring: bool):
    assert (
        KMPPrefixFallbackStructure(substring).contained_by(superstring)
        == substring_in_superstring
    )

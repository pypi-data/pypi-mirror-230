import pytest

from substring_structures import ACStringFSM


@pytest.mark.parametrize(
    "substrings,superstring,expected_substrings_in_superstring",
    [
        ({"a"}, "a", {"a"}),
        ({""}, "", {""}),
        ({"ba"}, "abab", {"ba"}),
        ({"b", "ba"}, "abab", {"b", "ba"}),
        ({"b", "ba", "aba"}, "abab", {"b", "ba", "aba"}),
        ({"b", "ba", "aba", "baba"}, "abab", {"b", "ba", "aba"}),
        ({"baba", "ab"}, "babad", {"baba", "ab"}),
    ],
)
def test_find_substrings_in_superstring(
    substrings: set[str],
    superstring: str,
    expected_substrings_in_superstring: set[str],
):
    assert (
        ACStringFSM(substrings).find_substrings_in_superstring(superstring)
        == expected_substrings_in_superstring
    )

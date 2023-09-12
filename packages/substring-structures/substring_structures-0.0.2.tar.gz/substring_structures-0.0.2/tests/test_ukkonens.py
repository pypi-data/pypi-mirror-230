import pytest

from substring_structures import SuffixTree


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
    suffix_tree = SuffixTree(superstring)
    actual_found_substrings = {
        substring for substring in substrings if substring in suffix_tree
    }
    assert actual_found_substrings == expected_substrings_in_superstring

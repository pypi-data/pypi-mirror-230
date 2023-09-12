# substring_structures

https://pypi.org/project/substring-structures/

Python library for substring search structures. Includes implementations of [Ukkonen's algorithm](https://en.wikipedia.org/wiki/Ukkonen%27s_algorithm), the [Aho-Corasick algorithm](https://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_algorithm),
and the [Knuth-Morris-Pratt algorithm](https://en.wikipedia.org/wiki/Knuth%E2%80%93Morris%E2%80%93Pratt_algorithm).

## Ukkonen's Suffix Tree

```py
>>> from substring_structures import SuffixTree

>>> hello = SuffixTree("hello")
>>> "lo" in hello
True
>>> "he" in hello
True
>>> "hi" in hello
False
```

Suffix tree implementation based on descriptions from https://www.charliemistrata.com/posts/ukkonens-algorithm.

This suffix tree can be precomputed for a string `S` in O(N) time using Ukkonen's algorithm.
It can then be used to check if a string `W` of length M is a substring of `S` in O(M) time.

## Aho-Corasick String Finite State Machine

```py
>>> from substring_structures import ACStringFSM

>>> greetings = ACStringFSM({"hello", "hi", "hey"})
>>> greetings.find_substrings_in_superstring(superstring="hi, hello")
{"hello", "hi"}
```

Structure used to preprocess a set of substrings to efficiently do substring checks.

Based on the [Aho-Corasick algorithm](https://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_algorithm),
this structure is an FSM (finite state machine) that can be computed in O(N) time for a set of
strings `strings` of total character count N. It can then be used to efficiently check which
strings in `strings` are in an arbitrary larger string `superstring` using the
`find_substrings_in_superstring(superstring)` method.

## Knuth-Morris-Pratt Prefix Fallback

```py
>>> from substring_structures import KMPPrefixFallback

>>> KMPPrefixFallback("bababooie")
KMPPrefixFallback(string='bababooie', fallback_length_by_prefix_length=[-1, 0, 0, 1, 2, 3, 0, 0, 0])
>>> baba = KMPPrefixFallback("baba")
>>> baba.contained_by("ababab")
True
>>> baba.contained_by("keke")
False
```

Structure used to preprocess a string `W` of length M in O(M) time so that you can check
if its a substring of another string `S` of length N in O(N) time using `KMPPrefixFallback(w).contained_by(s)`.

It does this by generating a structure of string W that allows you to "fallback" from a longer prefix of
W to a shorter prefix of W on a character mismatch when searching S. The code here
is based on descriptions at https://www.charliemistrata.com/posts/knuth-morris-pratt.

This class is mainly to illustrate the Knuth-Morris-Pratt algorithm as python has
a fast built-in algorithm for substring search.

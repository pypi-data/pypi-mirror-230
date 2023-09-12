from typing import Collection


class _ACNode:
    def __init__(self):
        self.values = set()
        self.children: dict[str, _ACNode] = {}
        self.suffix_link: _ACNode | None = None


class ACStringFSM:
    """
    Structure used to preprocess a set of substrings to efficiently do substring checks.

    Based on the Aho-Corasick algorithm (https://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_algorithm),
    this structure is an FSM (finite state machine) that can be computed in O(N) time for a set of
    strings `strings` of total character count N. It can then be used to efficiently check which
    strings in `strings` are in an arbitrary larger string `superstring` using the
    `find_substrings_in_superstring(superstring)` method.

    >>> greetings = ACStringFSM({"hello", "hi", "hey"})
    >>> greetings.find_substrings_in_superstring(superstring="hi, hello")
    {"hello", "hi"}
    """

    def __init__(self, strings: Collection[str]):
        if isinstance(strings, str):
            raise ValueError(
                f"'`strings` should be a collection of strings but was passed a single string '{strings}'."
            )
        self.strings = strings
        self._root = _ACNode()
        if "" in strings:
            self._root.values.add("")

        current_nodes_by_string = {string: self._root for string in strings}

        current_char_index = 0
        while any(current_nodes_by_string):
            strings_shorter_than_current_char_index = []
            for string, current_node in current_nodes_by_string.items():
                if current_char_index >= len(string):
                    strings_shorter_than_current_char_index.append(string)
                    continue

                current_char = string[current_char_index]

                # Add a new child node if it does not already exist.
                if current_char not in current_node.children:
                    child_node = _ACNode()
                    current_node.children[current_char] = child_node
                    child_node.suffix_link = self._move_forward_from_node(
                        node=current_node.suffix_link,
                        char=current_char,
                    )
                    child_node.values |= child_node.suffix_link.values
                else:
                    child_node = current_node.children[current_char]

                # Set the value of the child node to the current string if
                # we have reached the end of the string.
                at_last_char_of_string = current_char_index == len(string) - 1
                if at_last_char_of_string:
                    child_node.values.add(string)

                current_nodes_by_string[string] = child_node

            for (
                string_shorter_than_current_char_index
            ) in strings_shorter_than_current_char_index:
                current_nodes_by_string.pop(string_shorter_than_current_char_index)
            current_char_index += 1

    def _move_forward_from_node(self, node: _ACNode | None, char: str) -> _ACNode:
        """Move forward from node using char, traveling along suffix links where necessary."""
        while node != None:
            if char in node.children:
                return node.children[char]
            node = node.suffix_link

        # We have failed every recursive check, landing at the 'None'
        # suffix link of the root node.
        return self._root

    def find_substrings_in_superstring(self, superstring: str) -> set[str]:
        """Find which of `self.strings` occurs in `superstring`."""
        current_node = self._root
        found_substrings = set(current_node.values)

        for char in superstring:
            current_node = self._move_forward_from_node(current_node, char)
            found_substrings |= current_node.values

        return found_substrings

    def __str__(self) -> str:
        return f"AhoCorasickStringFSM(strings={self.strings})"

    def __repr__(self) -> str:
        return self.__str__()

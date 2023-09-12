from dataclasses import dataclass


class _STNode:
    """
    A node in a suffix tree, consisting of outgoing `STEdge`s to other `STNode`s keyed by character, and a
    fallback suffix link.
    """

    def __init__(self, incoming_branch):
        self.incoming_branch: _STBranch = incoming_branch
        self.outgoing_branches: dict[str, _STBranch] = {}
        self.suffix_link: _STNode | None = None

    def __str__(self):
        return str(self.outgoing_branches)

    def __repr__(self):
        return self.__str__()


class _STBranch:
    """
    An edge in a suffix tree, consisting of the position in the string the edge starts at, the length of the edge,
    and the `STNode` at the end of the edge.
    """

    def __init__(
        self,
        string: str,
        start_index_in_string: int,
        length: float = float("inf"),
        source_node: _STNode = None,
        destination_node: _STNode | None = None,
    ):
        self.string = string
        self.start_index_in_string = start_index_in_string
        self.length = length
        self.source_node = source_node
        self.destination_node = destination_node

    def __str__(self):
        end_index_in_string = min(
            len(self.string), self.start_index_in_string + self.length
        )
        return f"{self.string[:self.start_index_in_string]}|{self.string[self.start_index_in_string:end_index_in_string]}|{self.string[end_index_in_string:]}"

    def __repr__(self):
        return self.__str__()


@dataclass
class _STBranchPoint:
    branch: _STBranch
    branch_distance: int


class SuffixTree:
    """
    Suffix tree implementation based on descriptions from https://www.charliemistrata.com/posts/ukkonens-algorithm.

    This suffix tree can be precomputed for a string `S` in O(N) time using Ukkonen's algorithm.
    It can then be used to check if a string `W` of length M is a substring of `S` in O(M) time.

    >>> hello = SuffixTree("hello")
    >>> "lo" in hello
    True
    >>> "he" in hello
    True
    >>> "hi" in hello
    False
    """

    def __init__(self, string: str):
        self.string = string
        # By appending a '🍁' to the end of the string, we ensure we will
        # pay our branch debt at the end of creating the suffix tree, as we
        # won't be able to travel along any existing branch using '🍁'
        self._string = string + "🍁"
        self._root = _STNode(incoming_branch=None)
        self._tree_position: _STNode | _STBranchPoint = self._root
        self._current_suffix_length = 0
        self._next_index_in_string = 0

        self._done_constructing = False
        self._create_suffix_tree()
        self._done_constructing = True

    def _create_suffix_tree(self):
        # After each step of this loop, we should have a suffix tree
        # for a new prefix of the string (disregarding planned branches)
        for string_index, char in enumerate(self._string):
            self._next_index_in_string = string_index
            char

            # Keep track of the previously created junction node
            # for setting up suffix links.
            previously_created_junction_node_this_step: _STNode | None = None

            # Continue to grow out leaf branches from planned branches
            # as long as we are unable to continue growing them through
            # an existing branch.
            while not self._try_move_forward_one_in_tree(char):
                node_at_tree_position = self._get_or_create_node_at_position()

                # Link the previously created junction node's suffix link
                # to this node if applicable.
                if previously_created_junction_node_this_step is not None:
                    previously_created_junction_node_this_step.suffix_link = (
                        node_at_tree_position
                    )
                previously_created_junction_node_this_step = node_at_tree_position

                # Grow out a new branch.
                new_leaf_branch = _STBranch(
                    self._string,
                    start_index_in_string=self._next_index_in_string,
                    source_node=node_at_tree_position,
                )
                node_at_tree_position.outgoing_branches[char] = new_leaf_branch
                current_position_is_root = node_at_tree_position is self._root
                if current_position_is_root:
                    break

                # Update our position
                self._move_to_next_longest_suffix(node_at_tree_position)
            else:
                self._current_suffix_length += 1

    def _move_to_next_longest_suffix(self, current_node):
        self._current_suffix_length -= 1

        if current_node.suffix_link is not None:
            self._tree_position = current_node.suffix_link
        elif (
            type(self._tree_position) is _STNode
            and (
                parent_node_suffix_link := self._tree_position.incoming_branch.source_node.suffix_link
            )
            is not None
        ):
            node_distance_in_tree = (
                self._current_suffix_length
                + 1
                - self._tree_position.incoming_branch.length
            )
            self._move_to_correct_position_from_node(
                parent_node_suffix_link, node_distance_in_tree
            )
        else:
            self._move_to_correct_position_from_node(
                self._root, node_distance_in_tree=0
            )

    def _move_to_correct_position_from_node(
        self, node: _STNode, node_distance_in_tree: int
    ):
        distance_remaining = self._current_suffix_length - node_distance_in_tree
        if distance_remaining == 0:
            self._tree_position = node
            return

        # While growing out branches, our position is one before the character
        # we are using as the start of new branches.
        # Python ranges are closed open, so our end will be this index directly.
        current_suffix_end = self._next_index_in_string
        current_suffix_start = current_suffix_end - self._current_suffix_length
        current_string_index = current_suffix_start + node_distance_in_tree
        current_character = self._string[current_string_index]
        edge_to_move_along = node.outgoing_branches[current_character]

        if edge_to_move_along.length > distance_remaining:
            self._tree_position = _STBranchPoint(
                edge_to_move_along, distance_remaining - 1
            )
            return

        self._move_to_correct_position_from_node(
            edge_to_move_along.destination_node,
            node_distance_in_tree + edge_to_move_along.length,
        )

    def _try_move_forward_one_in_tree(self, char: str) -> bool:
        """Try to move forward from the current position, moving forward and returning True if possible."""
        # Try to move forward if we are at a node.
        if type(self._tree_position) is _STNode:
            if char not in self._tree_position.outgoing_branches:
                return False

            branch_to_move_onto = self._tree_position.outgoing_branches[char]
            if branch_to_move_onto.length == 1:
                self._tree_position = branch_to_move_onto.destination_node
            else:
                self._tree_position = _STBranchPoint(
                    branch_to_move_onto, branch_distance=0
                )
            return True

        # Try to move forward if we are on a branch.
        next_char_in_edge = self._string[
            self._tree_position.branch.start_index_in_string
            + self._tree_position.branch_distance
            + 1
        ]
        if char != next_char_in_edge:
            return False

        self._tree_position.branch_distance += 1
        if self._tree_position.branch_distance == self._tree_position.branch.length - 1:
            self._tree_position = self._tree_position.branch.destination_node
        return True

    def _get_or_create_node_at_position(self) -> _STNode:
        if type(self._tree_position) is _STNode:
            return self._tree_position
        return self._bisect_branch_at_position()

    def _bisect_branch_at_position(self) -> _STNode:
        assert type(self._tree_position) is _STBranchPoint
        branch_being_bisected = self._tree_position.branch
        pre_bisected_destination_node = self._tree_position.branch.destination_node
        pre_bisected_length = self._tree_position.branch.length

        # Reuse the existing edge as the first half, modifying some properties
        new_junction_node = _STNode(incoming_branch=branch_being_bisected)
        branch_being_bisected.destination_node = new_junction_node
        branch_being_bisected.length = self._tree_position.branch_distance + 1

        second_half_start_index_in_string = (
            branch_being_bisected.start_index_in_string + branch_being_bisected.length
        )
        new_second_half_branch = _STBranch(
            self._string,
            start_index_in_string=second_half_start_index_in_string,
            length=pre_bisected_length
            - branch_being_bisected.length,  # edge_being_bisected has been updated to be the first half
            source_node=new_junction_node,
            destination_node=pre_bisected_destination_node,
        )

        new_junction_node.outgoing_branches[
            self._string[second_half_start_index_in_string]
        ] = new_second_half_branch
        if pre_bisected_destination_node is not None:
            pre_bisected_destination_node.incoming_branch = new_second_half_branch

        return new_junction_node

    def contains(self, substring: str) -> bool:
        """Returns if the string used to construct this suffix tree contains substring."""
        self._tree_position = self._root
        for char in substring:
            if not self._try_move_forward_one_in_tree(char):
                return False
        return True

    def __contains__(self, item) -> bool:
        return isinstance(item, str) and self.contains(item)

    def __str__(self):
        """
        String representation of the suffix tree that changes
        as the suffix tree is being built, useful for understanding
        what's happening using a debugger.
        """
        if self._done_constructing:
            return f"SuffixTree('{self.string}')"
        longest_unbranched_suffix_start_in_string = (
            self._next_index_in_string - self._current_suffix_length
        )
        return (
            self._string[:longest_unbranched_suffix_start_in_string]
            + "|"
            + self._string[
                longest_unbranched_suffix_start_in_string : self._next_index_in_string
            ]
            + "["
            + self._string[self._next_index_in_string]
            + "]"
            + self._string[self._next_index_in_string + 1 :]
        )

    def __repr__(self) -> str:
        return self.__str__()

import json
from collections import deque
from typing import Tuple, Callable, Optional

from dupal import DuPalBase
from node import Node


def bstr_r(number: int, hi_z_mask: int = 0):
    binary_str = f"{number:08b}"
    mask_str = f"{hi_z_mask:08b}"
    result_str = "".join(
        "Z" if mask_str[i] == "1" else binary_str[i] for i in range(8)
    )
    return f"{result_str[:3]}_{result_str[3:7]}_{result_str[7:8]}"


class PalAnalyzer:
    def __init__(self, dupal_board: DuPalBase):
        self._dupal_board = dupal_board

    @staticmethod
    def _get_or_create_node(nodes: dict[str, Node], outputs: str) -> Tuple[Node, bool]:
        if outputs not in nodes:
            nodes[outputs] = Node(outputs, outlinks=[], clock_outlinks=[])
            return nodes[outputs], True
        return nodes[outputs], False

    @staticmethod
    def _find_path(
        path_cache: dict[str, Tuple[Node, list[int]]],
        nodes: dict[str, Node],
        start_node: Node,
        node_condition: Callable[[Node], bool],
    ) -> Tuple[Optional[Node], list[int]]:
        # check cache
        if start_node.outputs in path_cache:
            (node, path) = path_cache[start_node.outputs]
            if node_condition(node):
                return node, path

        queue = deque([(start_node, [])])
        visited = set()

        while queue:
            node, path = queue.popleft()

            if node_condition(node):
                return node, path

            visited.add(node.outputs)

            for inputs, outputs in node.outlinks + [
                (-(inputs + 1), outputs) for inputs, outputs in node.clock_outlinks
            ]:
                child_node = nodes.get(outputs)
                if child_node and child_node.outputs not in visited:
                    queue.append((child_node, path + [inputs]))

        return None, []

    def _walk_to(self, path: list[int]):
        for inputs in path:
            if inputs < 0:
                self._dupal_board.set_inputs(-inputs - 1)
                self._dupal_board.clock()
            else:
                self._dupal_board.set_inputs(inputs)

    @staticmethod
    def _save_states_to_file(nodes, file_name: str):
        data_json = json.dumps(nodes, default=lambda o: o.__dict__)
        # save to file
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(data_json)

    def analyze(self, output_file_name: str) -> bool:
        node_count = 0
        outlink_count = 0
        nodes: dict[str, Node] = {}
        path_cache: dict[str, Tuple[Node, list[int]]] = {}
        possible_inputs = [inputs for inputs in range(2**8)]
        outputs = bstr_r(self._dupal_board.set_inputs(0))  # we need to get hi-z mask here somehow
        node, _ = self._get_or_create_node(nodes, outputs)
        node_count += 1
        while True:
            # can we create outlink?
            if len(node.outlinks) < len(possible_inputs):
                inputs = possible_inputs[node.next_inputs_idx]
                outputs = bstr_r(self._dupal_board.set_inputs(inputs))  # we need to get hi-z mask here somehow
                node.outlinks.append((inputs, outputs))
                outlink_count += 1
                node.next_inputs_idx += 1
                child_node, node_created = self._get_or_create_node(nodes, outputs)
                nodes[outputs] = child_node
                node_count += 1 if node_created else 0
                node = nodes[outputs]
                print(
                    f"{outlink_count} / {node_count * len(possible_inputs) * 2} ({node_count} states)"
                )
            elif len(node.clock_outlinks) < len(
                possible_inputs
            ):  # should we trigger clock?
                inputs = possible_inputs[node.next_clock_inputs_idx]
                self._dupal_board.set_inputs(inputs)  # we need to get hi-z mask here somehow
                outputs = bstr_r(self._dupal_board.clock())
                node.clock_outlinks.append((inputs, outputs))
                outlink_count += 1
                node.next_clock_inputs_idx += 1
                child_node, node_created = self._get_or_create_node(nodes, outputs)
                nodes[outputs] = child_node
                node_count += 1 if node_created else 0
                node = nodes[outputs]
                print(
                    f"{outlink_count} / {node_count * len(possible_inputs) * 2} ({node_count} states)"
                )
            else:
                # can we walk to node that is not yet completely mapped out?
                start_node = node
                node, path = (
                    self._find_path(
                        path_cache,
                        nodes,
                        start_node,
                        lambda n: len(n.outlinks) + len(n.clock_outlinks)
                        < 2 * len(possible_inputs),
                    )
                    if outlink_count < node_count * len(possible_inputs) * 2
                    else (None, None)
                )
                assert not node or len(node.outlinks) + len(
                    node.clock_outlinks
                ) < 2 * len(possible_inputs), "We found a complete node"
                if node:
                    self._walk_to(path)
                    path_cache[start_node.outputs] = (node, path)
                else:  # can't find any incomplete node
                    # do we have everything we need?
                    done = False
                    if all(
                        len(node.outlinks) + len(node.clock_outlinks)
                        == 2 * len(possible_inputs)
                        for node in nodes.values()
                    ):
                        print("We have everything we need.")
                        done = True
                    else:
                        print(
                            "We don't have everything we need, but we can't do anything more without power-cycling."
                        )
                    total_outlinks = 0
                    for node in nodes.values():
                        total_outlinks += len(node.outlinks) + len(node.clock_outlinks)
                    print(f"Total outlinks: {total_outlinks}")
                    self._save_states_to_file(nodes, output_file_name)
                    return done

import json
from collections import deque
from typing import Tuple, Callable, Optional

from dupal import DuPalBase
from node import Node
from pal import Pal10L8, Pal16R4, Pal16L8


class PalAnalyzer:
    def __init__(self, dupal: DuPalBase):
        self._dupal = dupal

    @staticmethod
    def _get_or_create_node(nodes: dict[int, Node], outputs: int) -> Tuple[Node, bool]:
        if outputs not in nodes:
            nodes[outputs] = Node(outputs, outlinks=[], clock_outlinks=[])
            return nodes[outputs], True
        return nodes[outputs], False

    @staticmethod
    def _find_path(
        path_cache: dict[int, Tuple[Node, list[int]]],
        nodes: dict[int, Node],
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
                self._dupal.set_inputs(-inputs - 1)
                self._dupal.clock()
            else:
                self._dupal.set_inputs(inputs)

    @staticmethod
    def _save_states_to_file(nodes, file_name: str):
        data_json = json.dumps(nodes, default=lambda o: o.__dict__)
        # save to file
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(data_json)

    def _analyze_10l8(self, output_file_name: str):
        outputs = {}
        for inputs in range(2**10):
            outputs[inputs] = self._dupal.set_inputs(inputs)
            print(f"{inputs + 1} / {2**10}")
        data_json = json.dumps(outputs)
        with open(output_file_name, "w", encoding="utf-8") as file:
            file.write(data_json)

    def _analyze(
        self, output_file_name: str, exclude_clock_links: bool, inputs_range: int
    ) -> bool:
        node_count = 0
        outlink_count = 0
        nodes: dict[int, Node] = {}
        path_cache: dict[int, Tuple[Node, list[int]]] = {}
        possible_inputs = [inputs for inputs in range(inputs_range)]
        outputs = self._dupal.set_inputs(0)
        node, node_created = self._get_or_create_node(nodes, 0)
        node_count += 1 if node_created else 0
        multiplier = 2 if not exclude_clock_links else 1
        while True:
            # can we create outlink?
            if len(node.outlinks) < len(possible_inputs):
                inputs = possible_inputs[node.next_inputs_idx]
                outputs = self._dupal.set_inputs(inputs)
                node.outlinks.append((inputs, outputs))
                outlink_count += 1
                node.next_inputs_idx += 1
                child_node, node_created = self._get_or_create_node(nodes, inputs)
                nodes[outputs] = child_node
                node_count += 1 if node_created else 0
                node = nodes[outputs]
                print(
                    f"{outlink_count} / {node_count * len(possible_inputs) * multiplier} ({node_count} states)"
                )
            elif not exclude_clock_links and len(node.clock_outlinks) < len(
                possible_inputs
            ):  # should we trigger clock?
                inputs = possible_inputs[node.next_clock_inputs_idx]
                self._dupal.set_inputs(inputs)
                outputs = self._dupal.clock()
                node.clock_outlinks.append((inputs, outputs))
                outlink_count += 1
                node.next_clock_inputs_idx += 1
                child_node, node_created = self._get_or_create_node(nodes, inputs)
                nodes[outputs] = child_node
                node_count += 1 if node_created else 0
                node = nodes[outputs]
                print(
                    f"{outlink_count} / {node_count * len(possible_inputs) * multiplier} ({node_count} states)"
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
                        < multiplier * len(possible_inputs),
                    )
                    if outlink_count < node_count * len(possible_inputs) * multiplier
                    else (None, None)
                )
                assert not node or len(node.outlinks) + len(
                    node.clock_outlinks
                ) < multiplier * len(possible_inputs), "We found a complete node"
                if node:
                    self._walk_to(path)
                    path_cache[start_node.outputs] = (node, path)
                else:  # can't find any incomplete node
                    # do we have everything we need?
                    done = False
                    if all(
                        len(node.outlinks) + len(node.clock_outlinks)
                        == multiplier * len(possible_inputs)
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

    def analyze(self, output_file_name: str) -> bool:
        if isinstance(self._dupal.pal, Pal10L8):
            self._analyze_10l8(output_file_name)
            return True
        elif isinstance(self._dupal.pal, Pal16L8):
            return self._analyze(
                output_file_name,
                exclude_clock_links=True,
                inputs_range=self._dupal.pal.inputs_range,
            )
        elif isinstance(self._dupal.pal, Pal16R4):
            return self._analyze(
                output_file_name,
                exclude_clock_links=False,
                inputs_range=self._dupal.pal.inputs_range,
            )
        else:
            print("This PAL is not supported.")

import json
from collections import deque
from typing import Tuple, Callable, Optional

from analyzer import PalRAnalyzer
from node import NodeExt, Node
from pal import PalBase
from utils import AddOnceQueue, bcomb, bstr8


class PalRAnalyzerExt:
    def __init__(self, pal: PalBase):
        self._pal = pal

    def _walk_to(self, path: list[int]):
        for inputs in path:
            self._pal.read_outputs((inputs >> 1) << 1, clock=(inputs & 1) == 1)

    @staticmethod
    def _save_states_to_file(nodes: dict[str, NodeExt], file_name: str):
        data_json = json.dumps(
            nodes,
            default=lambda obj: None if isinstance(obj, AddOnceQueue) else obj.__dict__,
        )
        # save to file
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(data_json)

    def _get_or_create_node(
        self, nodes: dict[str, NodeExt], state: str
    ) -> Tuple[NodeExt, bool]:
        if state not in nodes:
            new_node = NodeExt(state, outlinks={}, inputs=AddOnceQueue())
            for inputs in range(2**9):
                new_node.inputs.add(inputs)
            nodes[state] = new_node
            return nodes[state], True
        return nodes[state], False

    @staticmethod
    def _find_path(
        path_cache: dict[str, Tuple[NodeExt, list[int]]],
        nodes: dict[str, NodeExt],
        start_node: NodeExt,
        node_condition: Callable[[NodeExt], bool],
    ) -> Tuple[Optional[NodeExt], list[int]]:
        # check cache
        if start_node.state in path_cache:
            (node, path) = path_cache[start_node.state]
            if node_condition(node):
                return node, path
        queue: deque[Tuple[NodeExt, list[int]]] = deque([(start_node, [])])
        visited = set[str]()
        while queue:
            node, path = queue.popleft()
            if node_condition(node):
                return node, path
            visited.add(node.state)
            seen_outputs = set()
            for inputs, outputs in node.outlinks.items():
                if outputs not in seen_outputs:
                    seen_outputs.add(outputs)
                    child_node = nodes.get(outputs)
                    if child_node and child_node.state not in visited:
                        queue.append((child_node, path + [inputs]))
        return None, []

    @staticmethod
    def _convert_state(state: str) -> int:
        return int(state.replace("_", "").replace("Z", "0"), 2) & 0b000_1111_0

    @staticmethod
    def check_states(file_name: str, reg_file_name: str = None) -> None:
        reg_data: dict[int, Node] = dict()
        simple_states = True
        with open(file_name, "r") as file:
            data: dict[str, dict] = json.load(file)
        for _, state_data in data.items():
            state = PalRAnalyzerExt._convert_state(state_data["state"])
            if state not in reg_data:
                print(f"Adding state {state}")
                reg_data[state] = Node(
                    state=state, outlinks={}, mappings={}, inputs=AddOnceQueue()
                )
                reg_data[state].outlinks = {
                    (int(k) >> 1) << 1: PalRAnalyzerExt._convert_state(v)
                    for k, v in state_data["outlinks"].items()
                    if (int(k) & 1) == 1
                }
                reg_data[state].mappings = {
                    int(k): v
                    for k, v in state_data["outlinks"].items()
                    if (int(k) & 1) != 1
                }
            else:
                print(f"Checking state {state}")
                outlinks = {
                    (int(k) >> 1) << 1: PalRAnalyzerExt._convert_state(v)
                    for k, v in state_data["outlinks"].items()
                    if (int(k) & 1) == 1
                }
                mappings = {
                    int(k): v
                    for k, v in state_data["outlinks"].items()
                    if (int(k) & 1) != 1
                }
                simple_states = (
                    simple_states
                    and mappings == reg_data[state].mappings
                    and outlinks == reg_data[state].outlinks
                )
        if reg_file_name:
            PalRAnalyzer.save_states_to_file(reg_data, reg_file_name)
        if simple_states:
            print(
                "The outputs seem to be INDEPENDENT of implicit combinatorial feedbacks."
            )
        else:
            print("WARNING: The outputs seem to DEPEND on combinatorial feedbacks.")

    @staticmethod
    def create_state_identifier(outputs: int, hi_z_mask: int) -> str:
        return bstr8(outputs, hi_z_mask)

    def analyze(self, output_file_name: str):
        nodes: dict[str, NodeExt] = dict[str, NodeExt]()
        path_cache: dict[str, Tuple[NodeExt, list[int]]] = dict[
            str, Tuple[NodeExt, list[int]]
        ]()
        last_save = 0
        outlinks_total = 0
        outlinks_done = 0
        outputs, hi_z_mask = self._pal.read_states(0)
        state = self.create_state_identifier(outputs, hi_z_mask)
        node, _ = self._get_or_create_node(nodes, state)
        outlinks_total += node.inputs.count
        while True:
            # can we create outlink?
            if not node.inputs.empty:
                inputs = node.inputs.dequeue()
                clock = (inputs & 1) == 1
                outputs, hi_z_mask = self._pal.read_states((inputs >> 1) << 1, clock)
                state = self.create_state_identifier(outputs, hi_z_mask)
                if not clock:
                    io_mask = 0b_111_0000_1
                    for io_inputs in bcomb(hi_z_mask & io_mask):
                        outlinks_total += node.inputs.add(
                            inputs ^ (io_inputs << 10)
                        ) + node.inputs.add((inputs ^ (io_inputs << 10)) | 1)
                node.outlinks[inputs] = state
                outlinks_done += 1
                child_node, node_created = self._get_or_create_node(nodes, state)
                outlinks_total += child_node.inputs.count if node_created else 0
                node = child_node
                print(f"{outlinks_done} / {outlinks_total} ({len(nodes)} states)")
                # perform intermediate writes to output file
                if outlinks_done - last_save >= 1000:
                    last_save = outlinks_done
                    self._save_states_to_file(nodes, output_file_name)
            else:
                # can we walk to node that is not yet completely mapped out?
                start_node = node
                node, path = (
                    self._find_path(
                        path_cache,
                        nodes,
                        start_node,
                        lambda _node: not _node.inputs.empty,
                    )
                    if outlinks_done < outlinks_total
                    else (None, None)
                )
                assert not node or not node.inputs.empty, "We found a complete node"
                if node:
                    self._walk_to(path)
                    path_cache[start_node.state] = (node, path)
                else:  # can't find any incomplete node
                    # do we have everything we need?
                    if all(node.inputs.empty for node in nodes.values()):
                        print("We have everything we need.")
                    else:
                        print(
                            "We don't have everything we need, but we can't do anything more without power-cycling."
                        )
                    print(f"Total outlinks: {outlinks_total}")
                    self._save_states_to_file(nodes, output_file_name)
                    return

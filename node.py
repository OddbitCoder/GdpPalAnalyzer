from dataclasses import dataclass

from utils import AddOnceQueue


@dataclass
class Node:
    state: int

    outlinks: dict[int, int]
    inputs: AddOnceQueue

    mappings: dict[int, str]


@dataclass
class NodeExt:
    state: str

    inputs: AddOnceQueue
    outlinks: dict[int, str]

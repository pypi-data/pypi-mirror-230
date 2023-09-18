from dataclasses import dataclass, field
from typing import List
from typing_extensions import Self
import logging


logger = logging.getLogger(__name__)


@dataclass
class Stack:
    name: str = ""
    children: List[Self] = field(default_factory=list)
    value: int = 0

    def pile_up(self, childstack: Self):
        self.value += childstack.value

        for exist_child in self.children:
            # added to exist, no need to create one
            if exist_child.name == childstack.name:
                for new_child in childstack.children:
                    exist_child.pile_up(new_child)
                return

        self.children.append(childstack)


def parse_location(locations, value):
    """
    recursive parse locations
    """
    location1, *rest = locations

    stack = Stack()
    stack.name = location1["Line"][0]["Function"]["Name"]
    stack.value = value
    if rest:
        stack.children = [parse_location(rest, value)]
    else:
        stack.children = []

    return stack


def parse_sample(sample):
    locations = reversed(sample["Location"])
    stack = parse_location(locations, value=sample["Value"][0])
    return stack


def debug_root(root: Stack, indent=0):
    num = str(indent)
    space = num + " " * (indent - len(num))
    logger.debug(f"{space}{root.name=} ({root.value})")
    for child in root.children:
        debug_root(child, indent + 2)


def parse_goroutine(data):
    samples = data["Sample"]
    root = Stack("root")
    for sample in samples:
        child_stack = parse_sample(sample)
        root.pile_up(child_stack)

    return root

from dataclasses import dataclass
from tree_sitter import Node


@dataclass()
class NodeInfo:
    node: Node
    parent_type: str
    parent_identifier: str

    def __init__(
        self, child_node: Node, parent_node: "NodeInfo" = None, file_str: str = None
    ):
        self.file_str = file_str
        self.node = child_node
        if parent_node is None:
            self.parent_type = "program"
            self.parent_identifier = "program"
        elif parent_node.parent_type == "program":
            self.parent_type = "root node"
            self.parent_identifier = "root node"
        else:
            parent_identifier = NodeInfo._get_identifier(parent_node.node, file_str)
            if parent_identifier is None:
                self.parent_type = parent_node.parent_type
                self.parent_identifier = parent_node.parent_identifier
            else: 
                self.parent_type = parent_node.node.type
                self.parent_identifier = parent_identifier

    def __str__(self):
        return f"\nnode_identifier:{NodeInfo._get_identifier(self.node, self.file_str)}\nparent_identifier:{self.parent_identifier}\parent_type:{self.parent_type}\nnode_type={self.node.type}"

    def __repr__(self):
        return self.__str__()

    @property
    def children(self):
        return self.node.children

    @staticmethod
    def _get_identifier(node: Node, file_str: str) -> str:
        for child in node.children:
            if child.type == "identifier":
                return file_str[child.start_byte : child.end_byte]
        return None

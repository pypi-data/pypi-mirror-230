# SPDX-FileCopyrightText: 2020 Roman Gilg <subdiff@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from subprocess import Popen, PIPE


class Node:
    def __init__(self, data):
        self.data = data
        self.identifier = data.identifier
        self.dependencies = set()

    def add_dependent(self, identifier):
        self.dependencies.add(identifier)


class Resolution:
    def __init__(self):
        self.nodes = {}

    def tsort_chain(self):
        """Use tsort to build a linear dependency chain."""
        tsort_input = ""
        for identifier, node in self.nodes.items():
            for dependency in node.dependencies:
                tsort_input += node.identifier + " " + dependency.identifier + " "

        tsort_byte_input = str.encode(tsort_input)

        with Popen(["tsort"], stdout=PIPE, stdin=PIPE) as tsort:
            tsort_output = tsort.communicate(input=tsort_byte_input)[0]

        if tsort.returncode != 0:
            raise

        tsort_output_list = tsort_output.decode().split("\n")
        return tsort_output_list[:-1]

    def make_partial_ordering_unique(self, identifier_chain, reverse_chain=False):
        """The input identifier_chain is a dependency chain with dependent elements later. But it
        is not unique, it is only a partial ordering. To get a unique ordering overlay
        additionally a lexicographical ordering."""

        node_chain = []

        # We remember for node element its dependent nodes in order.
        for i, identifier in enumerate(identifier_chain):
            node = self.nodes[identifier]
            node_struct = {"node": node, "dependents": []}

            for dependent in node.dependencies:
                chain_len = len(identifier_chain)
                for j in range(i + 1, chain_len):
                    if dependent.identifier == identifier_chain[j]:
                        node_struct["dependents"].append(dependent)
                        break

            node_chain.append(node_struct)

        # Append nodes without any dependencies. They might have not been in the initial
        # input variable identifier_chain.
        for key, node in self.nodes.items():
            found = False
            for node_struct in node_chain:
                if node == node_struct["node"]:
                    found = True
                    break
            if not found:
                node_chain.append({"node": node, "dependents": []})

        # Reverse the chain. This way dependencies are in front of the nodes that depend on them.
        node_chain.reverse()

        # Then we build subsets of nodes that don't have dependents, order these
        # lexicographically, add them to the result and make the remaining list to work on
        # independent of them. This way a new subset of nodes without dependents can be
        # identified and the method reapplied until all nodes have been prepended into
        # the resulting sorted list.
        sorted_nodes = []
        while len(node_chain):
            nodes_without_dependents = []

            for node_struct in reversed(node_chain):
                if not node_struct["dependents"]:
                    nodes_without_dependents.append(node_struct["node"])
                    node_chain.remove(node_struct)

            assert nodes_without_dependents
            nodes_without_dependents.sort(key=lambda node: node.identifier, reverse=reverse_chain)
            sorted_nodes = nodes_without_dependents + sorted_nodes

            # Now remove the dependents from other nodes (by that at least one
            # other node should have no dependents anymore).
            for node_struct in node_chain:
                for dependent in reversed(node_struct["dependents"]):
                    for node in nodes_without_dependents:
                        if dependent.identifier == node.identifier:
                            node_struct["dependents"].remove(dependent)
                            break

        if reverse_chain:
            sorted_nodes.reverse()

        return sorted_nodes

    def add_node(self, data):
        node = Node(data)
        self.nodes[node.identifier] = node
        return node

    def create_chain(self):
        tsort_output = self.tsort_chain()
        return self.make_partial_ordering_unique(tsort_output)

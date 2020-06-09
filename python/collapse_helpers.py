"""Provides services:
collapse_below(node): collapse_below starting at the given node
uncollapse_below(node): uncollapse at and below node
at_and_below_in(node): for selecting all IN nodes at and below node
at_and_above_in_uncollapsed(node): for selecting all IN nodes at and above node
"""

# A node's parent IN nodes
def _parent_in_nodes(node):
    parents = list()
    for edge in node.edge_list:
        if edge.dest_node == node and edge.relation == "IN":
            parents.append(edge.source_node)
    return parents

# A node's child IN nodes
def _child_in_nodes(node):
    children = list()
    for edge in node.edge_list:
        if edge.source_node == node and edge.relation == "IN":
            children.append(edge.dest_node)
    return children

# collapse_below starting at the given node
def collapse_below(node):
    if node.node_type == "R" or node.node_type == "C":
        # mark Root and Composite nodes with collapse_below flag
        node.collapse_below = True

    # get child IN nodes
    children = _child_in_nodes(node)

    for child in children:

        # see if the child has a parent that is not collapsed below
        parents = _parent_in_nodes(child)
        can_collapse_child = True
        for parent in parents:
            # Root and Composite parents can collapse below
            if parent.node_type == "R" or parent.node_type == "C":
                if not parent.collapse_below:
                    # do not collapse below this child
                    can_collapse_child = False

        if can_collapse_child:
            child.collapse = True
            collapse_below(child)

# uncollapse at and below node
def uncollapse_below(node):
    # uncollapse the node
    node.collapse = False
    node.collapse_below = False

    # uncollapse the node's IN children
    children = _child_in_nodes(node)

    for child in children:
        uncollapse_below(child)

def _below_in(node, node_set):
    children = _child_in_nodes(node)
    for child in children:
        node_set.add(child)
        _below_in(child, node_set)

# for selecting all IN nodes at and below node
def at_and_below_in(node):
    node_set = set()
    node_set.add(node)
    _below_in(node, node_set)
    return node_set

# ancestors IN bout not collapsed
def _above_in_uncollapsed(node, node_set):
    parents = _parent_in_nodes(node)
    for parent in parents:
        if not parent.collapse:
            node_set.add(parent)
        else:
            # follow above this parent
            _above_in_uncollapsed(parent, node_set)

# for selecting all IN nodes at and above node
def at_and_above_in_uncollapsed(node):
    node_set = set()
    if not node.collapse:
        node_set.add(node)
    else:
        _above_in_uncollapsed(node, node_set)
    return node_set

# get the set of removable_edges and addable_edge_pairs
def collapsed_edges(graph_item):
    print("collapsed_edges.a")

    # make sure there are edges to work with
    if not len(graph_item.edges):
        return (list(), list())

    # identify the existing collapsed source_node, dest_node edge pairs
    existing_edge_pairs = set()
    existing_edges = dict()
    for edge in graph_item.edges:
        if edge.relation == "COLLAPSED_FOLLOWS":
            existing_edge_pairs.add((edge.source_node, edge.dest_node))
            existing_edges[(edge.source_node, edge.dest_node)] = edge
            print("identified existing edge      %s     to     %s" % (edge.source_node.label, edge.dest_node.label))

    # calculate the set of source_node, dest_node edge pairs
    edge_pairs = set()
    for edge in graph_item.edges:
        if edge.relation == "FOLLOWS" and (edge.source_node.collapse
                                           or edge.dest_node.collapse):
            print("will add COLLAPSED_FOLLOWS to bridge: %s    to    %s" % (edge.source_node.label, edge.dest_node.label))
            # source and dest nodes
            source_node_set = at_and_above_in_uncollapsed(edge.source_node)
            dest_node_set = at_and_above_in_uncollapsed(edge.dest_node)
            for source_node in source_node_set:
                 for dest_node in dest_node_set:
                     if source_node != dest_node:
                         print("adding    %s        to         %s" % (source_node.label, dest_node.label))
                         edge_pairs.add((source_node, dest_node))

    # identify edges that need removed
    removable_edges = list()
    removable_pairs = existing_edge_pairs - edge_pairs
    for source_node, dest_node in removable_pairs:
        removable_edges.append(existing_edges[(source_node, dest_node)])

    # identify edges that need added
    addable_edge_pairs = edge_pairs - existing_edge_pairs

    return (removable_edges, addable_edge_pairs)


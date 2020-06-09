from collections import defaultdict
from PyQt5.QtCore import QLineF, QPointF

def _place_points(edge, count):
    scale = 20

    # edge connects same node
    if edge.source_id == edge.target_id:
        # origin point
        p = edge.mapFromItem(edge.source_node, 0, 0)

        # edge to same node so identify a length higher than the node
        h = 200 + 2*scale * count
        l = QLineF(QPointF(0,0), QPointF(h,0))
        # 0 degrees is at 3 o'clock, increasing clockwise
        l.setAngle(90+60)
        edge.cbp1 = p + l.p2()
        l.setAngle(90-60)
        edge.cbp2 = p + l.p2()

    # edge connects separate nodes
    else:

        # node points
        source_p = edge.mapFromItem(edge.source_node, 0, 0)
        dest_p = edge.mapFromItem(edge.dest_node, 0, 0)
        edge.cbp1 = (2*source_p + dest_p)/3 # 1/3 across
        edge.cbp2 = (source_p + 2*dest_p)/3 # 2/3 across

        # skew overlapping edges
        if count > 0:
            angle = QLineF(source_p, dest_p).angle()
            l = QLineF(QPointF(0,0), QPointF(scale * count,0))
            l.setAngle(angle+90)

            # bow depending on orientation of nodes
            if source_p.x() < dest_p.x() or \
                    (source_p.x() == dest_p.x() and source_p.y() > dest_p.y()):
                edge.cbp1 += l.p2()
                edge.cbp2 += l.p2()
            else:
                edge.cbp1 -= l.p2()
                edge.cbp2 -= l.p2()

"""Set Cubic Bezier points cbp1 and cbp2 for the edge if not already set."""
class EdgePointPlacer():

    def __init__(self):

        # placed edges keyed by (source_id lower, source_id higher) pair
        self.placed_edges = defaultdict(int)

    # place the cubic bezier points
    def place_cubic_bezier_points(self, edge):

        if edge.cbp1:
            # already placed
            return

        # identify key as (source_id lower, source_id higher) pair
        if edge.source_id < edge.target_id:
            key = (edge.source_id, edge.target_id)
        else:
            key = (edge.target_id, edge.source_id)

        count = self.placed_edges[key]
        _place_points(edge, count)
        self.placed_edges[key] += 1


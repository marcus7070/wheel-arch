from typing import Tuple, Literal
from OCP.GccAna import GccAna_Lin2d2Tan
from OCP.GccEnt import GccEnt
from OCP.gp import gp_Circ2d, gp_Ax22d, gp_Pnt2d, gp_Dir2d
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge2d
from OCP.Geom2dAPI import Geom2dAPI_InterCurveCurve
from OCP.Geom2d import Geom2d_Line, Geom2d_Circle, Geom2d_Curve
import cadquery as cq


def makeTangentCircles(
    center0: Tuple[float, float],
    radius0: float,
    center1: Tuple[float, float],
    radius1: float,
    sense0: Literal["outside", "inside"] = "outside",
    sense1: Literal["outside", "inside"] = "outside"
):
    solv_args = []
    geom_circs = []
    for c, r, s in [(center0, radius0, sense0), (center1, radius1, sense1)]:
        pnt = gp_Pnt2d(*c)
        d = gp_Dir2d(1.0, 0.0)
        ax = gp_Ax22d(pnt, d)
        circ = gp_Circ2d(ax, r)
        geom_circs.append(Geom2d_Circle(circ))
        qual_circ = GccEnt.Outside_s(circ) if s == "outside" else GccEnt.Enclosing_s(circ)
        solv_args.append(qual_circ)

    solver = GccAna_Lin2d2Tan(*solv_args, 1e-6)  # a tolerance
    if not solver.IsDone():
        raise RuntimeError("Solver not done")
    if solver.NbSolutions() != 1:
        raise RuntimeError("Multiple solutions")
    lin2d = solver.ThisSolution(1)  # this line is infinite, need to trim
    geom2d = Geom2d_Line(lin2d)
    pnts = []
    for c in geom_circs:
        intersector = Geom2dAPI_InterCurveCurve(geom2d, c)
        if intersector.NbPoints() != 1:
            raise RuntimeError("I expected one intersection point")
        pnts.append(intersector.Point(1))

    # now need to trim the line by these two points
    builder = BRepBuilderAPI_MakeEdge2d(lin2d, *pnts)
    return cq.Edge(builder.Edge())

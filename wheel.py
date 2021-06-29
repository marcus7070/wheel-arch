import cadquery as cq
from types import SimpleNamespace as d

dims = d()
dims.rim = d()
dims.rim.diam = 175
dims.rim.inserts = d()  # those little black inserts that the axle goes through
dims.rim.inserts.thick = 3
dims.rim.inserts.flange_od = 37.5
dims.rim.inserts.length = 24
dims.rim.inserts.id = 25.1
dims.rim.axle_diam = dims.rim.inserts.id + 2 * dims.rim.inserts.thick  # ie. OD of inserts
dims.rim.axle_width = 59.5
dims.tyre = d()
dims.tyre.od = 320
dims.tyre.width = 75


rim = (
    cq.Workplane("XZ")
    .move(0, dims.rim.axle_diam / 2)
    .hLine(dims.rim.axle_width / 2 - dims.rim.inserts.thick)
    .vLineTo(dims.rim.diam / 2)
    .hLineTo(0)
    .mirrorY()
    .revolve(axisStart=(0, 0), axisEnd=(1, 0))
)

tyre = (
    cq.Workplane("XZ")
    .spline(
        [
            (0, dims.tyre.od / 2),
            (dims.rim.axle_width / 2 - dims.rim.inserts.thick - 5, dims.rim.diam / 2),
        ],
        tangents=(cq.Vector(1.75, 0), cq.Vector(-1, -1)),
        scale=False,
    )
    .hLineTo(0)
    .mirrorY()
    .revolve(axisStart=(0, 0), axisEnd=(1, 0))
)

insert = (
    cq.Workplane()
    .circle(dims.rim.inserts.flange_od / 2)
    .extrude(dims.rim.inserts.length)
    .transformed(rotate=(180, 0, 0))
    .hole(dims.rim.inserts.id)
    .faces(">Z")
    .workplane()
    .circle(dims.rim.axle_diam / 2)
    .circle(dims.rim.inserts.flange_od / 2)
    .cutBlind(-(dims.rim.inserts.length - dims.rim.inserts.thick))
    .faces(">Z[1]")
    .tag("back_of_flange")
    .end()
)

assy = cq.Assembly(rim, name="rim", color=cq.Color(1.0, 0.1, 0.1, 0.95))
assy.add(tyre, name="tyre", color=cq.Color(0.1, 0.1, 0.1))
assy.constrain(
    "rim",
    cq.Face.makePlane(1, 1, dir=(1, 0, 0)),
    "tyre",
    cq.Face.makePlane(1, 1, dir=(1, 0, 0)),
    "Plane",
    param=0,
)
assy.add(insert, name="pos_insert", color=cq.Color(0.2, 0.2, 0.2))
assy.constrain("pos_insert?back_of_flange", "rim@faces@>X", "Plane")
assy.add(insert, name="neg_insert", color=cq.Color(0.2, 0.2, 0.2))
assy.constrain("neg_insert?back_of_flange", "rim@faces@<X", "Plane")
assy.solve()


if "show_object" in locals():
    show_object(assy)

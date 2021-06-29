import cadquery as cq
from types import SimpleNamespace as d
import leg
import wheel


dims = d()
dims.body = d()
dims.body.width = leg.dims.od
dims.body.backing_wall_thick = 10
dims.axle_diam = wheel.dims.rim.inserts.id
dims.bearing = d()
dims.bearing.thick = 3
dims.bearing.inner = d()
dims.bearing.inner.id = dims.axle_diam
dims.bearing.inner.shaft_od = dims.bearing.inner.id + dims.bearing.thick * 2
dims.bearing.inner.width = dims.body.width + dims.bearing.thick + 5
dims.bearing.outer = d()
dims.bearing.outer.id = dims.bearing.inner.shaft_od + 0.2
dims.bearing.outer.od = dims.bearing.outer.id + min(dims.bearing.thick + 0.2, 10 * 2)  # should be at least 10mm face
dims.bearing.inner.flange_od = dims.bearing.outer.od - 0.2
dims.bearing.outer.width = dims.body.width - dims.body.backing_wall_thick
dims.body.od = dims.bearing.outer.od + dims.body.backing_wall_thick * 2
dims.body.axle_hole_diam = dims.bearing.inner.shaft_od + 0.4
dims.body.leg_insertion = leg.dims.id * 1.5


bearing_inner = (
    cq.Workplane("YZ", origin=(-dims.bearing.thick, 0, 0))
    .circle(dims.bearing.inner.flange_od / 2)
    .extrude(dims.bearing.thick)
    .faces(">X")
    .workplane()
    .circle(dims.bearing.inner.shaft_od / 2)
    .extrude(dims.bearing.inner.width)
    .faces("<X")
    .workplane()
    .hole(dims.bearing.inner.id)
)

bearing_outer = (
    cq.Workplane("YZ")
    .circle(dims.bearing.outer.od / 2)
    .circle(dims.bearing.outer.id / 2)
    .extrude(dims.bearing.outer.width)
)

body = (
    cq.Workplane("YZ")
    .circle(dims.body.od / 2)
    .extrude(dims.body.width)
    .copyWorkplane(cq.Workplane(origin=(dims.body.width / 2, 0, 0)))
    .circle(dims.body.width / 2)
    .extrude(dims.body.od / 2 + dims.body.leg_insertion + 3)
    .faces("<X")
    .workplane()
    .hole(dims.bearing.outer.od, dims.bearing.outer.width)
    .faces("<X[1]")
    .tag("bearing_inner_face")
    .end()
    .faces("<X")
    .workplane()
    .hole(dims.body.axle_hole_diam)
    .faces(">Z")
    .workplane(centerOption="CenterOfMass")
    .circle(dims.body.width / 2)
    .circle(leg.dims.id / 2)
    .cutBlind(-dims.body.leg_insertion)
    .faces(">Z[-2]")
    .tag("leg_mount_face")
    .end()
    .center(0, 0)
    .hole(6, 10)
)

assy = cq.Assembly(body, name="body", color=cq.Color(0.05, 0.05, 0.05))
assy.add(bearing_outer, name="bearing_outer", color=cq.Color(1.0, 0.99, 0.82))
assy.add(bearing_inner, name="bearing_inner", color=cq.Color(1.0, 0.99, 0.82))
assy.constrain(
    "bearing_outer@faces@>X",
    "body?bearing_inner_face",
    "Plane",
)
assy.constrain(
    "bearing_inner@faces@>X[1]",
    "bearing_outer@faces@>X[0]",
    "Plane",
)
assy.solve()

if "show_object" in locals():
    show_object(assy)

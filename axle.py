import cadquery as cq
from types import SimpleNamespace as d
import wheel as wheel_module
import leg_end as leg_end_module

dims = d()
dims.axle = d()
dims.axle.od = wheel_module.dims.rim.inserts.id
dims.axle.id = 19.6
dims.axle.length = 150

axle = (
    cq.Workplane("YZ")
    .circle(dims.axle.od / 2)
    .circle(dims.axle.id / 2)
    .extrude(dims.axle.length / 2, both=True)
)

axle_plug = (
    cq.Workplane()
    .circle(dims.axle.id / 2)
    .extrude(dims.axle.id)
    .faces(">Z")
    .workplane()
    .circle(leg_end_module.dims.bearing.inner.flange_od / 2)
    .extrude(5)
)

axle_threaded_plug = (
    cq.Workplane()
    .circle(dims.axle.id / 2)
    .extrude(dims.axle.id)
    .faces(">Z")
    .workplane()
    .hole(12)  # representing an M20 threaded hole
)

axle_threaded_cap = (
    cq.Workplane()
    .circle(12 / 2)
    .extrude(20)
    .faces(">Z")
    .workplane()
    .circle(leg_end_module.dims.bearing.inner.flange_od / 2)
    .extrude(5)
    .faces("<Z[1]")
    .tag("mating_face")
    .end()
)

assy = cq.Assembly(axle, name="axle")
assy.add(axle_plug, name="axle_plug")
assy.constrain(
    "axle_plug@faces@<Z[1]",
    "axle@faces@>X",
    "Plane",
)
assy.add(axle_threaded_plug, name="axle_threaded_plug")
assy.constrain(
    "axle_threaded_plug@faces@>Z",
    "axle@faces@<X",
    "Plane",
    param=0,
)
assy.add(axle_threaded_cap, name="axle_threaded_cap")
assy.constrain(
    "axle_threaded_cap?mating_face",
    "axle_threaded_plug@faces@>Z",
    "Plane",
)

assy.add(wheel_module.assy, name="wheel_assy")
assy.constrain(
    "wheel_assy",
    cq.Face.makePlane(1, 1, dir=cq.Vector(1, 0, 0)),
    "axle",
    cq.Face.makePlane(1, 1, dir=cq.Vector(1, 0, 0)),
    "Plane",
    param=0,
)

assy.solve()

if "show_object" in locals():
    show_object(assy)

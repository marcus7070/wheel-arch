from itertools import product
import cadquery as cq
import wa0 as wa_module
import castor_bearing as castor_bearing_module
import leg as leg_module
import leg_end as leg_end_module
import axle as axle_module
import importlib
importlib.reload(axle_module)

assy = cq.Assembly(wa_module.part, name="wheel_arch", color=cq.Color(0.2, 0.2, 0.2))

assy.add(castor_bearing_module.outer_bearing, name="upper_outer_bearing", color=cq.Color(1.0, 0.99, 0.82))
assy.add(castor_bearing_module.inner_bearing, name="upper_inner_bearing", color=cq.Color(1.0, 0.99, 0.82))
assy.add(castor_bearing_module.outer_bearing, name="lower_outer_bearing", color=cq.Color(1.0, 0.99, 0.82))
assy.add(castor_bearing_module.inner_bearing, name="lower_inner_bearing", color=cq.Color(1.0, 0.99, 0.82))

for z_pos, r_pos in product(["upper", "lower"], ["inner", "outer"]):
    assy.constrain(
        "_".join([z_pos, r_pos, "bearing"]),
        cq.Face.makePlane(1, 1),
        "wheel_arch",
        wa_module.part._getTagged(f"{z_pos}_bearing_face").val(),
        "Plane",
        param=0,
    )

for side in ["left", "right"]:
    assy.add(leg_module.leg, name=f"{side}_leg", color=cq.Color(0, 0, 0))
    assy.constrain(
        f"{side}_leg@faces@>Z",
        f"wheel_arch?{side}_leg",
        "Plane",
    )
    assy.add(leg_end_module.assy, name=f"{side}_leg_end")
    assy.constrain(
        f"{side}_leg_end?leg_mount_face",
        f"{side}_leg@faces@<Z",
        "Plane",
    )
    val = -1 if side == "left" else 1
    assy.constrain(
        f"{side}_leg_end",
        cq.Face.makePlane(1, 1, dir=(1, 0, 0)),
        "wheel_arch",
        cq.Face.makePlane(1, 1, dir=(val, 0, 0)),
        "Axis",
    )

assy.add(axle_module.assy, name="axle_assy")
assy.constrain(
    "axle_assy",
    cq.Face.makePlane(1, 1, dir=cq.Vector(1, 0, 0)),
    "wheel_arch",
    cq.Face.makePlane(1, 1, dir=cq.Vector(1, 0, 0)),
    "Axis",
    param=0,
)
assy.constrain(
    "axle_assy",
    cq.Vertex.makeVertex(0, 0, 0),
    "left_leg_end",
    cq.Face.makePlane(1, 1, dir=cq.Vector(0, 0, 1)),
    "PointInPlane",
    param=0,
)
assy.constrain(
    "axle_assy",
    cq.Vertex.makeVertex(0, 0, 0),
    "left_leg_end",
    cq.Face.makePlane(1, 1, dir=cq.Vector(0, 1, 0)),
    "PointInPlane",
    param=0,
)
assy.constrain(
    "axle_assy",
    cq.Vertex.makeVertex(0, 0, 0),
    "wheel_arch",
    cq.Face.makePlane(1, 1, dir=cq.Vector(1, 0, 0)),
    "PointInPlane",
    param=0,
)

assy.solve()
if "show_object" in locals():
    show_object(assy)

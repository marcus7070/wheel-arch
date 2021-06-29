import cadquery as cq
from types import SimpleNamespace as d

dims = d()
dims.id = 30.0
dims.od = 55.0
dims.thick = 10  # TODO: check
dims.inner_edge_thick = dims.thick / 3

outer_bearing = (
    cq.Workplane("XZ")
    .move(dims.id / 2)
    .hLineTo(dims.od / 2)
    .vLine(dims.thick - dims.inner_edge_thick)
    .lineTo(dims.id / 2, dims.inner_edge_thick)
    .close()
    .revolve(axisStart=(0, 0), axisEnd=(0, 1))
)

inner_bearing = (
    cq.Workplane("XZ")
    .move(dims.id / 2, dims.inner_edge_thick)
    .lineTo(dims.od / 2, dims.thick - dims.inner_edge_thick)
    .vLineTo(dims.thick)
    .hLineTo(dims.id / 2)
    .close()
    .revolve(axisStart=(0, 0), axisEnd=(0, 1))
)

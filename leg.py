import cadquery as cq
from types import SimpleNamespace as d
import wheel

dims = d()
dims.od = 26.0
dims.id = 19.6
dims.length = wheel.dims.tyre.od / 2 + 30

leg = cq.Workplane().circle(dims.od / 2).circle(dims.id / 2).extrude(dims.length)

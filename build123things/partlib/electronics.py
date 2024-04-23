
from warnings import warn
import build123d as bd
from build123things import MountPoint, Thing
from build123things.materials import PCB, Aether, MixedMaterial

class SimpleFan (Thing):
    def __init__(self,
            width=40,
            length=40,
            height=10,
            hole_diameter=3.2,
            hole_outer_offset=4
        ) -> None:
        super().__init__(material=Aether())
        warn("Material of SimpleFan is a dummy.")

        self.sketch_outline:bd.Sketch = self.sketch_outline_eps(0)
        self.sketch_holes:bd.Sketch = bd.Sketch() + [ # type: ignore
                bd.Location((x,y)) * bd.Circle(radius=hole_diameter/2) for x,y in (
                    (width/2-hole_outer_offset,   length/2-hole_outer_offset),
                    (width/2-hole_outer_offset,  -length/2+hole_outer_offset),
                    (-width/2+hole_outer_offset,  length/2-hole_outer_offset),
                    (-width/2+hole_outer_offset, -length/2+hole_outer_offset),
                )]
        self.sketch_bay:bd.Sketch = bd.Circle(radius=38.5/2)
        self.body_simple = bd.extrude(self.sketch_outline-self.sketch_holes-self.sketch_bay, amount=-height)
        self.bbox = bd.extrude(self.sketch_outline, amount=-height)
        self.mount = MountPoint(bd.Location())

    def sketch_outline_eps(self, epsilon:float=0) -> bd.Sketch:
        return bd.Sketch() + bd.Rectangle(width=self.p.width+epsilon, height=self.p.length+epsilon)

    def result(self) -> bd.Part:
        return self.body_simple

class RaspberryPi4B (Thing):
    """ A model of RPI 4B. """

    def __init__(self,
            outline_width = 85,
            outline_height = 56,
            pcb_thickness = 2,
        ) -> None:

        # Outlie and PCB
        _:bd.Sketch = bd.Sketch() +bd.Location((outline_width/2,outline_height/2)) * bd.Rectangle(height=outline_height, width=outline_width)
        self.pcb_sketch:bd.Sketch = bd.Sketch() + bd.fillet(_.vertices(), radius=3)
        for x,y in ((3.5, 3.5),(3.5+58,3.5),(3.5,3.5+49),(3.5+58,3.5+49)):
            self.pcb_sketch -= bd.Sketch() + bd.Location((x,y)) * bd.Circle(radius=1)
        self.pcb = bd.extrude(self.pcb_sketch, amount=-pcb_thickness)

        # Connections
        self.eth_location:bd.Location = bd.Location((89-10, 45.75, 13.5/2), (0,0,0))
        self.eth = self.eth_location * bd.Box(21.35, 15.59, 13.5)
        self.usb1 = bd.Location((89-10, 27, 8)) * bd.Box(17.43, 13.13, 16)
        self.usb2 = bd.Location((89-10, 9, 8)) * bd.Box(17.43, 13.13, 16)
        self.gpio = bd.Location((3.5+29, 3.5+49, 8.5/2)) * bd.Box(58-3.5*2-1, 6, 8.5)
        self.usbc = bd.Location((3.5+7.7, 3, 3.2/2)) * bd.Box(8.68, 7.44, 3.2)

        self.mount_center_below = bd.Location((outline_width/2, outline_height/2, -pcb_thickness),(180,0,0))

class L298n (Thing):
    """ Dual H-bridge. """

    def __init__(self,
            width = 43,
            height = 43,
            pcb_thickness = 2,
            hole_span = 37,
            hole_radius = 1.7,
        ) -> None:

        super().__init__(Aether())

        # Outline and PCB
        self.pcb_sketch:bd.Sketch = bd.Sketch() + bd.Rectangle(height=height, width=width, align=bd.Align.CENTER)
        pcb_mount_holes:bd.Sketch = bd.Sketch()
        for x,y in ((1,1),(1,-1),(-1,1),(-1,-1)):
            x = x * hole_span/2
            y = y * hole_span/2
            pcb_mount_holes += bd.Sketch() + bd.Location((x,y)) * bd.Circle(radius=hole_radius)
        self.pcb_mount_holes = pcb_mount_holes

        pcb = bd.extrude(self.pcb_sketch, amount=-pcb_thickness)
        pcb -= bd.extrude(self.pcb_mount_holes, amount=-pcb_thickness)
        self.pcb = pcb

        self.chip = bd.Location((-width/2, -height/2)) * bd.Location((width-17.5/2,height/2,17.5/2)) * bd.Box(17.5, 30, 17.5)
        self.out1 = bd.Location((-width/2, -height/2)) * bd.Location((width-30,height-2.5,5)) * bd.Box(10, 5, 10)
        self.out2 = bd.Location((-width/2, -height/2)) * bd.Location((width-30,2.5,5)) * bd.Box(10, 5, 10)
        self.pwr = bd.Location((-width/2, -height/2)) * bd.Location((2.5,height-5-7.5,5)) * bd.Box(5, 15, 10)
        self.mount_center = MountPoint(bd.Location((0,0,-pcb_thickness),(180,0,0)))

        self.body = self.pcb + self.chip + self.out1 + self.out2 + self.pwr

    def result(self) -> bd.Part:
        return self.body

class StepUp150W (Thing):
    def __init__(self,
            x_size_pcb = 65,
            x_size_heatsink = 42,
            y_size_pcb = 37,
            y_size_heatsink = 10,
            z_size_heatsink = 20,
            y_spacing_heatsink = 22,
            x_hole_span = 59,
            y_hole_span = 27,
            hole_diameter = 3.2,
            pcb_thickness = 1.7,
            x_size_ports = 7.5,
            y_size_ports = 5,
            z_size_ports = 10,
        ) -> None:

        # Outline and PCB
        self.sketch_pcb:bd.Sketch = bd.Sketch() + bd.Rectangle(width=x_size_pcb, height=y_size_pcb, align=bd.Align.CENTER)
        self.sketch_mount_holes:bd.Sketch = bd.Sketch() + [bd.Location((x[0]*x_hole_span/2,x[1]*y_hole_span/2)) * bd.Circle(radius=hole_diameter/2) for x in ((1,1),(1,-1),(-1,1),(-1,-1))] # type: ignore
        self.sketch_heatsinks:bd.Sketch = bd.Sketch() + [bd.Location((0,a*(y_spacing_heatsink/2+y_size_heatsink/2))) * bd.Rectangle(width=x_size_heatsink, height=y_size_heatsink) for a in (-1,1)] # type: ignore
        self.sketch_ports:bd.Sketch = [bd.Location((-x_size_pcb/2+x_size_ports/2,a*y_size_ports)) * bd.Rectangle(width=x_size_ports, height=y_size_ports) for a in (-.5,-1.5,.5,1.5)] # type: ignore

        self.pcb:bd.Part = bd.extrude(self.sketch_pcb - self.sketch_mount_holes, amount=-pcb_thickness)
        self.heatsinks:bd.Part = bd.extrude(self.sketch_heatsinks, amount=z_size_heatsink)
        self.ports:bd.Part = bd.extrude(bd.Sketch() + self.sketch_ports, amount=z_size_ports) # type: ignore

        self.mount_center:bd.Location = bd.Location((0,0,-pcb_thickness),(180,0,90))

    def result(self) -> bd.Part:
        return bd.Part() + [p[1] for p in self.enumerate_components_with_names(d0=False, d1=False, d2=False, d3=True)]

class LM2596 (Thing):
    """ Step-Down power convertor. """
    def __init__(self,
            pcb_size_x = 44,
            pcb_size_y = 22,
            pcb_size_z = 1.5,
            hole_span_x = 30,
            hole_span_y = 15,
            hole_diameter = 3.2,
            cond_diam = 8,
            cond_span = 34,
            cond_height = 10,
        ) -> None:

        super().__init__(MixedMaterial())

        # Outline and PCB
        self.sketch_pcb:bd.Sketch = bd.Sketch() + bd.Rectangle(width=pcb_size_x, height=pcb_size_y, align=bd.Align.CENTER)
        self.sketch_mount_holes:bd.Sketch = bd.Sketch() + [bd.Location((x[0]*hole_span_x/2,x[1]*hole_span_y/2)) * bd.Circle(radius=hole_diameter/2) for x in ((1,-1),(-1,1))] # type: ignore
        self.sketch_conds:bd.Sketch = bd.Sketch() + [bd.Location((a*(cond_span/2), 0)) * bd.Circle(radius=cond_diam/2) for a in (-1,1)] # type: ignore

        self.pcb:bd.Part = bd.extrude(self.sketch_pcb - self.sketch_mount_holes, amount=-pcb_size_z)
        self.conds:bd.Part = bd.extrude(self.sketch_conds, amount=cond_height)

        self.mount_center = MountPoint(bd.Location((0,0,-pcb_size_z),(180,0,90)))

        self.body = self.pcb + self.conds

    def result(self) -> bd.Part:
        return self.body

class DF62 (Thing):
    """ A three-way terminal block. """
    def __init__(self,
            size_z = 13,
            primary_size_x=33,
            primary_size_y=17,
            secondary_size_x=13,
            secondary_size_y=13,
            hole_span = 21,
            hole_offset_y = 3,
            hole_diameter = 3.2,
            hole_size_z = 5,
            hole_mass_diameter = 6,
        ) -> None:
        super().__init__(MixedMaterial())

        # Outline and PCB
        self.sketch:bd.Sketch = bd.Sketch() + \
                bd.Location((0,primary_size_y/2)) * bd.Rectangle(width=primary_size_x, height=primary_size_y) + \
                bd.Location((0,-secondary_size_y/2)) * bd.Rectangle(width=secondary_size_x, height=secondary_size_y)

        self.sketch_mount_holes = bd.Sketch() + [bd.Location((a * hole_span/2, -hole_diameter)) * bd.Circle(radius=hole_diameter/2) for a in (1,-1)] # type: ignore

        sketch_around_holes:bd.Sketch = bd.Sketch() + \
                bd.Location((hole_span/2, -hole_diameter)) * bd.Circle(radius=hole_mass_diameter/2) + \
                bd.Location((secondary_size_x/2,-hole_offset_y/2)) * bd.Rectangle(width=hole_diameter*3, height=hole_diameter) - \
                self.sketch_mount_holes


        self.sketch_around_holes = sketch_around_holes + bd.mirror(sketch_around_holes, about=bd.Plane.YZ)

        self.body = bd.extrude(self.sketch, amount=size_z) + bd.extrude(self.sketch_around_holes, amount=hole_size_z)

        self.mount_center = MountPoint(bd.Location((0,0,0),(180,0,90)))

    def result(self) -> bd.Part:
        return self.body

class RaspberryPiZeroWH (Thing):
    def __init__(self,
            x_size=65,
            y_size=30,
            mount_hole_offset=3.5,
            mount_hole_diameter=2.7,
            pcb_thickness=1.5,
        ) -> None:
        super().__init__(material=PCB())

        hole_locations = (
                (mount_hole_offset,mount_hole_offset),(x_size-mount_hole_offset,mount_hole_offset),(mount_hole_offset,y_size-mount_hole_offset),(x_size-mount_hole_offset,y_size-mount_hole_offset))

        self.sketch_mount_holes:bd.Sketch = bd.Sketch() + [bd.Location((x[0],x[1])) * bd.Circle(radius=mount_hole_diameter/2) for x in hole_locations] # type: ignore

        self.sketch_base:bd.Sketch = (
            bd.Sketch() + bd.fillet(bd.Rectangle(width=x_size, height=y_size, align=bd.Align.MIN).vertices(),radius=3) -
            self.sketch_mount_holes
        )

        self.sketch_gpio:bd.Sketch = bd.Sketch() + bd.Location((x_size/2,y_size-mount_hole_offset)) * bd.Rectangle(width=52,height=5)
        self.sketch_usb1:bd.Sketch = bd.Sketch() + bd.Location((41.4,3)) * bd.Rectangle(width=7.5,height=6)
        self.sketch_usb2:bd.Sketch = bd.Sketch() + bd.Location((54.0,3)) * bd.Rectangle(width=7.5,height=6)
        self.sketch_hdmi:bd.Sketch = bd.Sketch() + bd.Location((12.4,3.75)) * bd.Rectangle(width=11,height=7.5)
        self.sketch_sdcard:bd.Sketch = bd.Sketch() + bd.Location((6,16.9)) * bd.Rectangle(width=16,height=12)
        self.sketch_csi2:bd.Sketch = bd.Sketch() + bd.Location((x_size-1.5,15)) * bd.Rectangle(width=4,height=17)

        self.body:bd.Part = (
            bd.extrude(self.sketch_base,amount=-1.5) +
            bd.extrude(self.sketch_gpio,amount=9) +
            bd.extrude(self.sketch_usb1+self.sketch_usb2,amount=2.5) +
            bd.extrude(self.sketch_hdmi,amount=3) +
            bd.extrude(self.sketch_sdcard,amount=1) +
            bd.extrude(self.sketch_csi2,amount=1)
        )

        self.mount_center = MountPoint(bd.Location((x_size/2,y_size/2,-pcb_thickness),(180,0,0)))

    def result(self) -> bd.Part:
        return self.body

if "show_object" in globals().keys():
    #r = RaspberryPi4B()
    #r = SimpleFan()
    r = RaspberryPiZeroWH()
    #r = LM2596()
    #r = StepUp150W()
    #r = DF62()

    r.show_everything(show_object) #type:ignore


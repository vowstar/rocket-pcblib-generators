# USON-10_2.5x1.0mm_P0.5mm

TI DQA0010A. Height is the 0.55 mm maximum. Terminal length 0.365 mm is the midpoint of 0.30–0.43 mm. The drawing does not specify body standoff. The model uses 0.02 mm for display.

Body dimensions are 2.5 x 1.0 mm. Pin pitch is 0.5 mm.
Signal terminals are 0.2 mm wide. Ground terminals 3 and 8 are 0.4 mm wide.
Pin 3 includes the R0.125 inner projection. Other rounded terminals use R0.075.
Pin 1 is rectangular, as permitted by the package drawing.
The source constructs all geometry. It does not import the previous STEP model.

The contact plane is Z=0. Pin 1 matches the footprint's lower-left pad in KiCad top view.
The index mark size, colors, and unmodeled internal structure do not define manufacturing tolerances.

The PCB land pattern uses 0.20 x 0.565 mm signal pads and two 0.40 x 0.565 mm
ground pads at Y = +/-0.4175 mm. Signal paste matches the copper. Each
ground pad uses a separate 0.36 x 0.565 mm paste aperture. Copper corners
use R0.05. TI's NSMD example permits up to 0.07 mm mask expansion.
The footprint inherits the board mask setting.

[Manufacturer dimensions](https://www.ti.com/lit/ds/symlink/tpd4e02b04.pdf).

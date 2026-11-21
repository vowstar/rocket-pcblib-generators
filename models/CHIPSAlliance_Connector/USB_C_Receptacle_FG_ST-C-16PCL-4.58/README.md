# Fugangs FG-ST-C-16PCL-4.58

FreeCAD model for C51912219. Dimensions are from the [Fugangs outline drawing](https://datasheet.lcsc.com/datasheet/pdf/d92c6bc9c33cebdecef5aa2393552efc.pdf?productCode=C51912219).

- The mating axis is −Y. The front face sits at Y = −7 mm, the board seating surface is Z = 0, and the centre of the mating opening is at Z = 4.58 mm.
- The mouth envelope is 3.16 × 8.94 mm, the nominal body length is 14.00 mm, and the reinforcement reaches Z = 9.88 mm.
- The four shield tabs use a 4.06 × 6.10 mm pattern. The two Ø0.60 mm locators are 7.15 mm apart. The shield tabs and locator pegs extend into the PCB below the seating plane.

The shell seams, latches, tongue contact profiles and undimensioned locator depth are simplified for board assembly and enclosure clearance models. Use a physical connector and plug for latch, mating and tolerance-stack validation. The geometry is constructed from primitive solids and contains no lettering or logos.

## Appearance

The [LCSC photographs](https://item.szlcsc.com/54613016.html) show a satin silver shield and an exposed black rear support. The drawing specifies nickel over SUS304, black LCP, gold mating contacts and gold flash at the solder tails. The colours approximate those finishes under neutral lighting. STEP records the display colours. The metallic and roughness settings in `model.toml` describe the finish for physically based previews.

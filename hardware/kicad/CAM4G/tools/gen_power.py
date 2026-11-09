import re
import uuid

BASE = r"C:\Users\vuong\Documents\deepseek-harness\default-workspace\4g-camera\hardware\kicad\CAM4G"
CAM = BASE + r"\libs\CAM4G.kicad_sym"
DEV = r"C:\Users\vuong\AppData\Local\Programs\KiCad\10.0\share\kicad\symbols\Device.kicad_sym"
PWR = r"C:\Users\vuong\AppData\Local\Programs\KiCad\10.0\share\kicad\symbols\power.kicad_sym"
OUT = BASE + r"\power.kicad_sch"

SHEET_UUID = str(uuid.uuid4())


def extract(text, name):
    key = f'(symbol "{name}"'
    i = text.index(key)
    depth = 0
    j = i
    while True:
        c = text[j]
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                return text[i:j + 1]
        j += 1


def pins_of(block):
    out = []
    pat = re.compile(r'\(pin\s+\S+\s+\S+\s+\(at\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\).*?\(number\s+"([^"]+)"', re.S)
    for m in pat.finditer(block):
        out.append((m.group(4), float(m.group(1)), float(m.group(2))))
    return out


cam_text = open(CAM, encoding="utf-8").read()
dev_text = open(DEV, encoding="utf-8").read()
pwr_text = open(PWR, encoding="utf-8").read()

sym_blocks = {}
pin_maps = {}
for nm in ["TPS61088", "TPS62840", "INA226", "CN3058E"]:
    key = f"CAM4G:{nm}" if f'(symbol "CAM4G:{nm}"' in cam_text else nm
    b = extract(cam_text, key)
    b = b.replace(f'(symbol "{key}"', f'(symbol "CAM4G:{nm}"', 1)
    sym_blocks[f"CAM4G:{nm}"] = b
    pin_maps[f"CAM4G:{nm}"] = pins_of(b)

for nm in ["R", "C", "L", "LED"]:
    b = extract(dev_text, nm)
    b2 = b.replace(f'(symbol "{nm}"', f'(symbol "Device:{nm}"', 1)
    sym_blocks[f"Device:{nm}"] = b2
    pin_maps[f"Device:{nm}"] = pins_of(b2)

b = extract(pwr_text, "PWR_FLAG")
b2 = b.replace('(symbol "PWR_FLAG"', '(symbol "power:PWR_FLAG"', 1)
sym_blocks["power:PWR_FLAG"] = b2
pin_maps["power:PWR_FLAG"] = pins_of(b2)

# ---------------- component instances ----------------
# (ref, value, libid, x, y, {pin: net})
COMPS = []


def ic(ref, val, lib, x, y, nets):
    COMPS.append((ref, val, lib, x, y, nets))


ic("U2", "TPS61088", "CAM4G:TPS61088", 120, 90, {
    "1": "VCC_BOOST", "2": "BOOST_EN", "3": "FSW_BOOST",
    "4": "SW_BOOST", "5": "SW_BOOST", "6": "SW_BOOST", "7": "SW_BOOST",
    "8": "BOOT_BOOST", "9": "VBAT", "10": "SS_BOOST",
    "11": "GND", "12": "GND", "13": "GND",
    "14": "+5V_SYS", "15": "+5V_SYS", "16": "+5V_SYS",
    "17": "FB_BOOST", "18": "COMP_BOOST", "19": "ILIM_BOOST",
    "20": "GND", "21": "GND",
})

ic("U3", "TPS62840", "CAM4G:TPS62840", 660, 90, {
    "1": "GND", "2": "VBAT", "3": "GND", "4": "BUCK_EN",
    "5": "VSET_BUCK", "6": "GND", "7": "SW_BUCK", "8": "+3V3", "9": "GND",
})

ic("U5", "CN3058E", "CAM4G:CN3058E", 120, 260, {
    "1": "TEMP_NTC", "2": "ISET", "3": "GND", "4": "VBUS_5V",
    "5": "VBAT", "6": "CHG_DONE", "7": "CHG_STAT", "8": "VBAT", "9": "GND",
})

ic("U4", "INA226", "CAM4G:INA226", 660, 260, {
    "1": "GND", "2": "GND", "3": "INA_ALERT", "4": "I2C_SDA",
    "5": "I2C_SCL", "6": "+3V3", "7": "GND", "8": "VBAT",
    "9": "VBAT", "10": "VBAT_BMS",
})

# passives: (ref, value, symbol, x, y, pin1net, pin2net)
PASS = [
    ("C1", "10uF", "Device:C", 60, 160, "VBAT", "GND"),
    ("C2", "100nF", "Device:C", 95, 160, "VBAT", "GND"),
    ("C3", "3.3uF", "Device:C", 130, 160, "VCC_BOOST", "GND"),
    ("C6", "100nF", "Device:C", 165, 160, "BOOT_BOOST", "SW_BOOST"),
    ("C7", "47nF", "Device:C", 200, 160, "SS_BOOST", "GND"),
    ("C9", "1uF", "Device:C", 235, 160, "+5V_SYS", "GND"),
    ("C4", "47uF", "Device:C", 270, 160, "+5V_SYS", "GND"),
    ("R1", "178k", "Device:R", 305, 160, "+5V_SYS", "FB_BOOST"),
    ("R2", "56k", "Device:R", 340, 160, "FB_BOOST", "GND"),
    ("R3", "267k", "Device:R", 375, 160, "FSW_BOOST", "SW_BOOST"),
    ("R4", "64.9k", "Device:R", 410, 160, "ILIM_BOOST", "GND"),
    ("R5", "10.5k", "Device:R", 445, 160, "COMP_BOOST", "COMP_MID"),
    ("C5", "2.2nF", "Device:C", 480, 160, "COMP_MID", "GND"),
    ("C8", "DNP", "Device:C", 515, 160, "COMP_BOOST", "GND"),
    ("L1", "1.2uH", "Device:L", 550, 160, "VBAT", "SW_BOOST"),

    ("C10", "4.7uF", "Device:C", 620, 160, "VBAT", "GND"),
    ("C11", "10uF", "Device:C", 655, 160, "+3V3", "GND"),
    ("R6", "267k", "Device:R", 690, 160, "VSET_BUCK", "GND"),
    ("L2", "2.2uH", "Device:L", 725, 160, "SW_BUCK", "+3V3"),

    ("C13", "10uF", "Device:C", 60, 330, "VBUS_5V", "GND"),
    ("C14", "10uF", "Device:C", 95, 330, "VBAT", "GND"),
    ("R10", "1.2k", "Device:R", 130, 330, "ISET", "GND"),
    ("R13", "7.15k", "Device:R", 165, 330, "TEMP_NTC", "VBUS_5V"),
    ("R11", "1k", "Device:R", 200, 330, "VBUS_5V", "LED_CHG_A"),
    ("R12", "1k", "Device:R", 235, 330, "VBUS_5V", "LED_DONE_A"),
    ("D1", "RED", "Device:LED", 270, 330, "CHG_STAT", "LED_CHG_A"),
    ("D2", "GRN", "Device:LED", 305, 330, "CHG_DONE", "LED_DONE_A"),
    ("NTC1", "10k B3950", "Device:R", 340, 330, "TEMP_NTC", "GND"),

    ("R7", "0.05R", "Device:R", 620, 330, "VBAT_BMS", "VBAT"),
    ("C12", "100nF", "Device:C", 655, 330, "+3V3", "GND"),
    ("R8", "4.7k", "Device:R", 690, 330, "I2C_SDA", "+3V3"),
    ("R9", "4.7k", "Device:R", 725, 330, "I2C_SCL", "+3V3"),
]

PWR_FLAGS = [
    ("GND", 60, 400), ("VBUS_5V", 140, 400), ("+3V3", 220, 400),
]


def snap(v):
    return round(v / 1.27) * 1.27


def sym_instance(ref, val, lib, x, y, nets, dnp=False):
    x = snap(x)
    y = snap(y)
    u = str(uuid.uuid4())
    lines = []
    lines.append("\t(symbol")
    lines.append(f'\t\t(lib_id "{lib}")')
    lines.append(f'\t\t(at {x} {y} 0)')
    lines.append("\t\t(unit 1)")
    lines.append("\t\t(exclude_from_sim no)")
    lines.append("\t\t(in_bom yes)")
    lines.append("\t\t(on_board yes)")
    lines.append(f'\t\t(dnp {"yes" if dnp else "no"})')
    lines.append(f'\t\t(uuid "{u}")')
    lines.append(f'\t\t(property "Reference" "{ref}" (at {x} {y-12} 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'\t\t(property "Value" "{val}" (at {x} {y-9.5} 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'\t\t(property "Footprint" "" (at {x} {y} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    lines.append(f'\t\t(property "Datasheet" "" (at {x} {y} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    for num, _, _ in pin_maps[lib]:
        lines.append(f'\t\t(pin "{num}" (uuid "{uuid.uuid4()}"))')
    lines.append("\t\t(instances")
    lines.append('\t\t\t(project ""')
    lines.append(f'\t\t\t\t(path "/{SHEET_UUID}"')
    lines.append(f'\t\t\t\t\t(reference "{ref}")')
    lines.append("\t\t\t\t\t(unit 1)")
    lines.append("\t\t\t\t)")
    lines.append("\t\t\t)")
    lines.append("\t\t)")
    lines.append("\t)")
    body = "\n".join(lines)

    labels = []
    for num, px, py in pin_maps[lib]:
        net = nets.get(num)
        if not net:
            continue
        ax = x + px
        ay = y - py
        labels.append(f'\t(label "{net}" (at {ax:.3f} {ay:.3f} 0)\n'
                      f'\t\t(effects (font (size 1.0 1.0)) (justify left bottom))\n'
                      f'\t\t(uuid "{uuid.uuid4()}")\n\t)')
    return body, labels


blocks = []
for ref, val, lib, x, y, nets in COMPS:
    b, l = sym_instance(ref, val, lib, x, y, nets)
    blocks.append(b)
    blocks.extend(l)
for ref, val, lib, x, y, n1, n2 in PASS:
    b, l = sym_instance(ref, val, lib, x, y, {"1": n1, "2": n2}, dnp=(val == "DNP"))
    blocks.append(b)
    blocks.extend(l)
for net, x, y in PWR_FLAGS:
    b, l = sym_instance(f"#FLG{len(blocks)}", "PWR_FLAG", "power:PWR_FLAG", x, y, {"1": net})
    blocks.append(b)
    blocks.extend(l)

libs = "\n".join(sym_blocks.values())

header = f'''(kicad_sch
	(version 20231120)
	(generator "eeschema")
	(generator_version "8.0")
	(uuid "{SHEET_UUID}")
	(paper "A1")
	(title_block
		(title "CAM4G Power Sheet")
		(date "2026-11-09")
		(rev "0.2")
		(company "CAM4G")
	)
	(lib_symbols
{libs}
	)
'''

notes = []
notes.append('\t(text "BOOST 5V - TPS61088" (at 60 40 0) (effects (font (size 2 2)) (justify left bottom)) (uuid "' + str(uuid.uuid4()) + '"))')
notes.append('\t(text "BUCK 3V3 - TPS62840" (at 600 40 0) (effects (font (size 2 2)) (justify left bottom)) (uuid "' + str(uuid.uuid4()) + '"))')
notes.append('\t(text "CHARGER LFP - CN3058E" (at 60 220 0) (effects (font (size 2 2)) (justify left bottom)) (uuid "' + str(uuid.uuid4()) + '"))')
notes.append('\t(text "INA226" (at 600 220 0) (effects (font (size 2 2)) (justify left bottom)) (uuid "' + str(uuid.uuid4()) + '"))')

footer = '''
	(sheet_instances
		(path "/"
			(page "1")
		)
	)
)
'''

text = header + "\n".join(notes) + "\n" + "\n".join(blocks) + footer

with open(OUT, "w", encoding="utf-8") as f:
    f.write(text)

print("written", OUT, len(text))
for k, v in pin_maps.items():
    print(k, len(v), "pins")


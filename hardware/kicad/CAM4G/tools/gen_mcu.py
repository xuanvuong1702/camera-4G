import re
import uuid

BASE = r"C:\Users\vuong\Documents\deepseek-harness\default-workspace\4g-camera\hardware\kicad\CAM4G"
LIBDIR = r"C:\Users\vuong\AppData\Local\Programs\KiCad\10.0\share\kicad\symbols"
ROOT = BASE + r"\CAM4G.kicad_sch"


def match_block(text, start_idx):
    depth = 0
    j = start_idx
    while True:
        c = text[j]
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                return j
        j += 1


def extract(text, name):
    key = f'(symbol "{name}"'
    i = text.index(key)
    j = match_block(text, i)
    return text[i:j + 1]


def pins_of(block):
    out = []
    pat = re.compile(r'\(pin\s+\S+\s+\S+\s+\(at\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\).*?\(number\s+"([^"]+)"', re.S)
    for m in pat.finditer(block):
        out.append((m.group(4), float(m.group(1)), float(m.group(2))))
    return out


# ---- MCU symbol ----
MCU_PINS = [
    ("1", "PB9"), ("2", "PC14"), ("3", "PC15"), ("4", "NRST"), ("5", "VDDA"),
    ("6", "PA0"), ("7", "PA1"), ("8", "PA2"), ("9", "PA3"), ("10", "PA4"),
    ("11", "PA5"), ("12", "PA6"), ("13", "PA7"), ("14", "PB1"), ("15", "VSS"),
    ("16", "VDD"), ("17", "PA9"), ("18", "PA10"), ("19", "PA13"), ("20", "PA14"),
]


def make_mcu_symbol():
    n = len(MCU_PINS)
    half = n // 2
    height = half * 2.54 + 5.08
    top = height / 2 - 2.54
    L = ['\t(symbol "CAM4G:STM32L011F4"', '\t\t(exclude_from_sim no)', '\t\t(in_bom yes)', '\t\t(on_board yes)',
         f'\t\t(property "Reference" "U" (at 0 {height/2+2.54:.2f} 0) (effects (font (size 1.27 1.27))))',
         f'\t\t(property "Value" "STM32L011F4" (at 0 {height/2+5.08:.2f} 0) (effects (font (size 1.27 1.27))))',
         '\t\t(property "Footprint" "Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
         '\t\t(property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
         '\t\t(property "Description" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
         '\t\t(symbol "STM32L011F4_0_1"',
         f'\t\t\t(rectangle (start -10.16 {height/2:.2f}) (end 10.16 {-height/2:.2f}) (stroke (width 0.254) (type default)) (fill (type background)))',
         '\t\t)',
         '\t\t(symbol "STM32L011F4_1_1"']
    # pins: first 10 left, next 10 right
    body_pins = []
    for i, (num, nm) in enumerate(MCU_PINS):
        if i < half:
            y = top - i * 2.54
            body_pins.append((num, nm, -15.24, y, 0))
        else:
            y = top - (i - half) * 2.54
            body_pins.append((num, nm, 15.24, y, 180))
    for num, nm, x, y, ang in body_pins:
        L.append(f'\t\t\t(pin passive line (at {x:.2f} {y:.2f} {ang}) (length 5.08)')
        L.append(f'\t\t\t\t(name "{nm}" (effects (font (size 1.27 1.27))))')
        L.append(f'\t\t\t\t(number "{num}" (effects (font (size 1.27 1.27))))')
        L.append('\t\t\t)')
    L.append('\t\t)')
    L.append('\t)')
    return "\n".join(L), [(p[0], p[2], p[3]) for p in body_pins]


mcu_text = open(f"{LIBDIR}\\MCU_ST_STM32L0.kicad_sym", encoding="utf-8").read()
mcu_block = extract(mcu_text, "STM32L011F_3-4_Px").replace(
    '(symbol "STM32L011F_3-4_Px"', '(symbol "MCU_ST_STM32L0:STM32L011F_3-4_Px"', 1)
mcu_pins = pins_of(mcu_block)
MCU_LIB = "MCU_ST_STM32L0:STM32L011F_3-4_Px"

# ---- other symbols ----
dev_text = open(f"{LIBDIR}\\Device.kicad_sym", encoding="utf-8").read()
extra = {}
for nm in ["Battery_Cell", "D_Schottky", "R", "C"]:
    b = extract(dev_text, nm).replace(f'(symbol "{nm}"', f'(symbol "Device:{nm}"', 1)
    extra[f"Device:{nm}"] = b

conn_text = open(f"{LIBDIR}\\Connector_Generic.kicad_sym", encoding="utf-8").read()
for nm in ["Conn_01x03", "Conn_01x04"]:
    b = extract(conn_text, nm).replace(f'(symbol "{nm}"', f'(symbol "Connector_Generic:{nm}"', 1)
    extra[f"Connector_Generic:{nm}"] = b

conntext = open(f"{LIBDIR}\\Connector.kicad_sym", encoding="utf-8").read()
b = extract(conntext, "TestPoint").replace('(symbol "TestPoint"', '(symbol "Connector:TestPoint"', 1)
extra["Connector:TestPoint"] = b

root = open(ROOT, encoding="utf-8").read()
ROOT_UUID = re.search(r'\(uuid "([0-9a-f\-]+)"\)', root).group(1)

pin_maps = {k: pins_of(v) for k, v in extra.items()}
pin_maps[MCU_LIB] = mcu_pins


def sym_instance(ref, val, lib, x, y, nets, dnp=False, ref_dy=-12):
    x = round(x / 1.27) * 1.27
    y = round(y / 1.27) * 1.27
    u = str(uuid.uuid4())
    L = ["\t(symbol", f'\t\t(lib_id "{lib}")', f'\t\t(at {x} {y} 0)', "\t\t(unit 1)",
         "\t\t(exclude_from_sim no)", "\t\t(in_bom yes)", "\t\t(on_board yes)",
         f'\t\t(dnp {"yes" if dnp else "no"})', f'\t\t(uuid "{u}")',
         f'\t\t(property "Reference" "{ref}" (at {x} {y+ref_dy} 0) (effects (font (size 1.27 1.27))))',
         f'\t\t(property "Value" "{val}" (at {x} {y+ref_dy+2.54} 0) (effects (font (size 1.27 1.27))))',
         f'\t\t(property "Footprint" "" (at {x} {y} 0) (effects (font (size 1.27 1.27)) (hide yes)))',
         f'\t\t(property "Datasheet" "" (at {x} {y} 0) (effects (font (size 1.27 1.27)) (hide yes)))']
    for num, _, _ in pin_maps[lib]:
        L.append(f'\t\t(pin "{num}" (uuid "{uuid.uuid4()}"))')
    L += ["\t\t(instances", '\t\t\t(project ""', f'\t\t\t\t(path "/{ROOT_UUID}"',
          f'\t\t\t\t\t(reference "{ref}")', "\t\t\t\t\t(unit 1)", "\t\t\t\t)", "\t\t\t)", "\t\t)", "\t)"]
    body = "\n".join(L)

    labels = []
    for num, px, py in pin_maps[lib]:
        ax = x + px
        ay = y - py
        net = nets.get(num)
        if not net:
            labels.append(f'\t(no_connect (at {ax:.3f} {ay:.3f}) (uuid "{uuid.uuid4()}"))')
            continue
        labels.append(f'\t(label "{net}" (at {ax:.3f} {ay:.3f} 0)\n'
                      f'\t\t(effects (font (size 1.0 1.0)) (justify left bottom))\n'
                      f'\t\t(uuid "{uuid.uuid4()}")\n\t)')
    return body, labels


COMPS = []
COMPS.append(("U6", "STM32L011F4", MCU_LIB, 200, 900, {
    "1": "MCU_BOOT0", "2": "MODEM_RESET", "3": None, "4": "MCU_NRST", "5": "+3V3",
    "6": "PIR_OUT", "7": "ONEWIRE", "8": "MODEM_PWRKEY", "9": "MODEM_STATUS",
    "10": "MODEM_EN", "11": "BOOST_EN", "12": "SOC_READY", "13": "INA_ALERT",
    "14": "VBAT_SENSE", "15": "GND", "16": "+3V3", "17": "I2C_SCL",
    "18": "I2C_SDA", "19": "SWDIO", "20": "SWCLK",
}))
COMPS.append(("R25", "10k", "Device:R", 140, 980, {"1": "MCU_BOOT0", "2": "GND"}))
COMPS.append(("C17", "100nF", "Device:C", 180, 980, {"1": "+3V3", "2": "GND"}))
COMPS.append(("C18", "1uF", "Device:C", 220, 980, {"1": "+3V3", "2": "GND"}))
COMPS.append(("C19", "100nF", "Device:C", 260, 980, {"1": "MCU_NRST", "2": "GND"}))
COMPS.append(("J12", "DEBUG UART", "Connector_Generic:Conn_01x03", 320, 980, {"1": "DBG_TX", "2": "DBG_RX", "3": "GND"}))
COMPS.append(("J13", "SWD", "Connector_Generic:Conn_01x04", 380, 980, {"1": "+3V3", "2": "SWDIO", "3": "SWCLK", "4": "GND"}))
COMPS.append(("D5", "BAT54", "Device:D_Schottky", 440, 980, {"2": "+3V3", "1": "+3V3_RTC"}))
COMPS.append(("D6", "BAT54", "Device:D_Schottky", 480, 980, {"2": "BT1_P", "1": "+3V3_RTC"}))
COMPS.append(("BT1", "CR1220", "Device:Battery_Cell", 520, 980, {"1": "BT1_P", "2": "GND"}))
COMPS.append(("C16", "100nF", "Device:C", 560, 980, {"1": "+3V3_RTC", "2": "GND"}))
COMPS.append(("R31", "0R", "Device:R", 600, 980, {"1": "BUCK_EN", "2": "VBAT"}))
COMPS.append(("R32", "0R", "Device:R", 640, 980, {"1": "USB_DP", "2": "USB_MODEM_DP"}))
COMPS.append(("R33", "0R", "Device:R", 680, 980, {"1": "USB_DM", "2": "USB_MODEM_DM"}))
COMPS.append(("R34", "10k", "Device:R", 720, 980, {"1": "+5V_SYS", "2": "VBUS_DET"}))
COMPS.append(("R35", "10k", "Device:R", 760, 980, {"1": "VBUS_DET", "2": "GND"}))
COMPS.append(("TP1", "TP_3V3", "Connector:TestPoint", 800, 980, {"1": "TP_3V3"}))
COMPS.append(("TP2", "TP_1V8", "Connector:TestPoint", 840, 980, {"1": "TP_1V8"}))

blocks = []
for ref, val, lib, x, y, nets in COMPS:
    if lib not in pin_maps:
        continue
    b, l = sym_instance(ref, val, lib, x, y, nets, ref_dy=(16 if lib == MCU_LIB else -12))
    blocks.append(b)
    blocks.extend(l)

new_libs = [mcu_block] + [b for n, b in extra.items() if f'(symbol "{n}"' not in root]
i = root.index("(lib_symbols")
j = match_block(root, i)
root = root[:j] + "\n" + "\n".join(new_libs) + "\n\t" + root[j:]

k = root.index("\t(sheet_instances")
root = root[:k] + "\n".join(blocks) + "\n" + root[k:]

root = root.replace('(paper "A0")', '(paper "User" 1400 1150)')

open(ROOT, "w", encoding="utf-8").write(root)
print("mcu added; comps", len(COMPS), "libs", len(new_libs))

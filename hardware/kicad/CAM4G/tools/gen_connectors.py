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


SRC = {
    "Connector": ["USB_C_Receptacle_USB2.0_16P", "Micro_SD_Card"],
    "Connector_Generic": ["Conn_01x02", "Conn_01x03", "Conn_01x20", "Conn_02x06_Odd_Even"],
    "Switch": ["SW_Push"],
    "Device": ["Q_PMOS", "Q_NPN", "Q_NMOS", "R", "C", "LED"],
}

root = open(ROOT, encoding="utf-8").read()
ROOT_UUID = re.search(r'\(uuid "([0-9a-f\-]+)"\)', root).group(1)

sym_blocks = {}
pin_maps = {}
for lib, names in SRC.items():
    text = open(f"{LIBDIR}\\{lib}.kicad_sym", encoding="utf-8").read()
    for nm in names:
        full = f"{lib}:{nm}"
        b = extract(text, nm).replace(f'(symbol "{nm}"', f'(symbol "{full}"', 1)
        sym_blocks[full] = b
        pin_maps[full] = pins_of(b)

# ---------------- components ----------------
COMPS = []


def add(ref, val, lib, x, y, nets, dnp=False):
    COMPS.append((ref, val, lib, x, y, nets, dnp))


add("J1", "USB-C", "Connector:USB_C_Receptacle_USB2.0_16P", 100, 680, {
    "A1": "GND", "A12": "GND", "B1": "GND", "B12": "GND",
    "A4": "VBUS_5V", "A9": "VBUS_5V", "B4": "VBUS_5V", "B9": "VBUS_5V",
    "A5": "USB_CC1", "B5": "USB_CC2",
    "A6": "USB_DBG_DP", "B6": "USB_DBG_DP",
    "A7": "USB_DBG_DM", "B7": "USB_DBG_DM",
    "SH": "GND",
})
add("R14", "5.1k", "Device:R", 170, 680, {"1": "USB_CC1", "2": "GND"})
add("R15", "5.1k", "Device:R", 200, 680, {"1": "USB_CC2", "2": "GND"})

add("J4", "microSD", "Connector:Micro_SD_Card", 250, 680, {
    "1": "SD_D2", "2": "SD_D3", "3": "SD_CMD", "4": "+3V3",
    "5": "SD_CLK", "6": "GND", "7": "SD_D0", "8": "SD_D1", "SH": "GND",
})

add("J11", "MODEM", "Connector_Generic:Conn_02x06_Odd_Even", 380, 680, {
    "1": "+5V_MODEM", "2": "GND", "3": "USB_MODEM_DP", "4": "USB_MODEM_DM",
    "5": "MODEM_PWRKEY", "6": "MODEM_STATUS", "7": "MODEM_RESET", "8": "GND",
    "9": "MODEM_UART_TX", "10": "MODEM_UART_RX", "11": "+3V3", "12": "GND",
})

add("J3", "CAM 20P", "Connector_Generic:Conn_01x20", 500, 680, {
    "1": "GND", "2": "CAM_MCLK", "3": "GND",
    "4": "CAM_MIPI_D0_P", "5": "CAM_MIPI_D0_N", "6": "GND",
    "7": "CAM_MIPI_CK_P", "8": "CAM_MIPI_CK_N", "9": "GND",
    "10": "CAM_MIPI_D1_P", "11": "CAM_MIPI_D1_N", "12": "GND",
    "13": "CAM_SCL", "14": "CAM_SDA", "15": "GND",
    "16": "CAM_RESET", "17": "GND", "18": "GND",
    "19": "+3V3", "20": "+3V3",
})

add("J6", "PIR", "Connector_Generic:Conn_01x03", 600, 680, {"1": "+3V3", "2": "PIR_OUT", "3": "GND"})
add("J7", "IR LED", "Connector_Generic:Conn_01x02", 640, 680, {"1": "+5V_SYS", "2": "IR_LED_K"})
add("J8", "IR-CUT", "Connector_Generic:Conn_01x02", 680, 680, {"1": "IRCUT_A", "2": "IRCUT_B"})
add("J9", "DS18B20", "Connector_Generic:Conn_01x03", 720, 680, {"1": "+3V3", "2": "ONEWIRE", "3": "GND"})
add("J10", "DS18B20", "Connector_Generic:Conn_01x03", 760, 680, {"1": "+3V3", "2": "ONEWIRE", "3": "GND"})
add("J2", "BAT", "Connector_Generic:Conn_01x02", 800, 680, {"1": "VBAT_BMS", "2": "GND"})

# modem power switch
add("Q1", "AO3401", "Device:Q_PMOS", 860, 680, {"S": "+5V_SYS", "G": "MODEM_GATE", "D": "+5V_MODEM"})
add("R16", "100k", "Device:R", 900, 680, {"1": "+5V_SYS", "2": "MODEM_GATE"})
add("Q2", "2N3904", "Device:Q_NPN", 940, 680, {"B": "MODEM_B", "C": "MODEM_GATE", "E": "GND"})
add("R17", "10k", "Device:R", 980, 680, {"1": "MODEM_EN", "2": "MODEM_B"})
add("R18", "100k", "Device:R", 1010, 680, {"1": "MODEM_B", "2": "GND"})

# IR LED driver
add("Q3", "IRLZ44N", "Device:Q_NMOS", 1060, 680, {"D": "IR_LED_K", "G": "IR_GATE", "S": "GND"})
add("R19", "100R", "Device:R", 1100, 680, {"1": "IR_PWM", "2": "IR_GATE"})
add("R20", "100k", "Device:R", 1130, 680, {"1": "IR_GATE", "2": "GND"})

# reset + LEDs + SD card detect
add("SW1", "RESET", "Switch:SW_Push", 100, 790, {"1": "RESET_N", "2": "GND"})
add("R23", "10k", "Device:R", 140, 790, {"1": "+3V3", "2": "RESET_N"})
add("C15", "100nF", "Device:C", 180, 790, {"1": "RESET_N", "2": "GND"})
add("R24", "0R", "Device:R", 220, 790, {"1": "SD_CD", "2": "GND"})
add("R21", "1k", "Device:R", 260, 790, {"1": "+3V3", "2": "LED_PWR_A"})
add("D3", "PWR", "Device:LED", 300, 790, {"2": "LED_PWR_A", "1": "GND"})


def snap(v):
    return round(v / 1.27) * 1.27


def sym_instance(ref, val, lib, x, y, nets, dnp=False):
    x = snap(x)
    y = snap(y)
    u = str(uuid.uuid4())
    L = ["\t(symbol", f'\t\t(lib_id "{lib}")', f'\t\t(at {x} {y} 0)', "\t\t(unit 1)",
         "\t\t(exclude_from_sim no)", "\t\t(in_bom yes)", "\t\t(on_board yes)",
         f'\t\t(dnp {"yes" if dnp else "no"})', f'\t\t(uuid "{u}")',
         f'\t\t(property "Reference" "{ref}" (at {x} {y-12} 0) (effects (font (size 1.27 1.27))))',
         f'\t\t(property "Value" "{val}" (at {x} {y-9.5} 0) (effects (font (size 1.27 1.27))))',
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


blocks = []
for ref, val, lib, x, y, nets, dnp in COMPS:
    b, l = sym_instance(ref, val, lib, x, y, nets, dnp)
    blocks.append(b)
    blocks.extend(l)

# add only symbols not already embedded
new_libs = [b for name, b in sym_blocks.items() if f'(symbol "{name}"' not in root]
i = root.index("(lib_symbols")
j = match_block(root, i)
root = root[:j] + "\n" + "\n".join(new_libs) + "\n\t" + root[j:]

k = root.index("\t(sheet_instances")
root = root[:k] + "\n".join(blocks) + "\n" + root[k:]

root = root.replace('(paper "A1")', '(paper "A0")')

open(ROOT, "w", encoding="utf-8").write(root)
print("added libs:", len(new_libs), "components:", len(COMPS))

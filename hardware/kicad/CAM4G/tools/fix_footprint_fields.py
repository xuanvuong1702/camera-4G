import re
import pcbnew

BASE = r"C:\Users\vuong\Documents\deepseek-harness\default-workspace\4g-camera\hardware\kicad\CAM4G"
BOARD = BASE + r"\CAM4G.kicad_pcb"
SCH = BASE + r"\CAM4G.kicad_sch"

LIB = {
    "SOT-23": "Package_TO_SOT_SMD",
    "R_0603_1608Metric": "Resistor_SMD",
    "R_2512_6332Metric": "Resistor_SMD",
    "C_0603_1608Metric": "Capacitor_SMD",
    "LED_0603_1608Metric": "LED_SMD",
    "D_SOD-323": "Diode_SMD",
    "L_Bourns-SRN8040_8x8.15mm": "Inductor_SMD",
    "L_Bourns-SRN4018": "Inductor_SMD",
    "USB_C_Receptacle_HRO_TYPE-C-31-M-12": "Connector_USB",
    "Hirose_FH12-20S-0.5SH_1x20-1MP_P0.50mm_Horizontal": "Connector_FFC-FPC",
    "microSD_HC_Hirose_DM3AT-SF-PEJM5": "Connector_Card",
    "SW_SPST_B3S-1000": "Button_Switch_SMD",
    "Battery_Panasonic_CR1220-VCN_Vertical_CircularHoles": "Battery",
    "TestPoint_Pad_1.5x1.5mm": "TestPoint",
    "MSOP-10_3x3mm_P0.5mm": "Package_SO",
    "SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.3mm": "Package_SO",
    "TSSOP-20_4.4x6.5mm_P0.65mm": "Package_SO",
    "Core1106-SMT": "Core1106",
    "VQFN20_3.5": "CAM4G",
    "DLC0008B": "CAM4G",
}


def libfor(item):
    if item.startswith("JST_VH") or item.startswith("JST_XH"):
        return "Connector_JST"
    if item.startswith("PinHeader_2x06_P1.27"):
        return "Connector_PinHeader_1.27mm"
    if item.startswith("PinHeader_1x03_P2.54") or item.startswith("PinHeader_1x04_P2.54"):
        return "Connector_PinHeader_2.54mm"
    return LIB.get(item, "")


board = pcbnew.LoadBoard(BOARD)
ref2fp = {}
for fp in board.GetFootprints():
    item = str(fp.GetFPID().GetLibItemName())
    lib = libfor(item)
    ref2fp[fp.GetReference()] = (lib + ":" + item) if lib else item


def block_end(text, k):
    depth = 0
    j = k
    while True:
        c = text[j]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return j
        j += 1


text = open(SCH, encoding="utf-8").read()
out = []
i = 0
changed = 0
while True:
    k = text.find("(symbol", i)
    if k < 0:
        out.append(text[i:])
        break
    if "(lib_id" not in text[k:k + 300]:
        out.append(text[i:k + 7])
        i = k + 7
        continue
    j = block_end(text, k)
    blk = text[k:j + 1]
    m = re.search(r'\(property "Reference" "([^"]+)"', blk)
    if m and m.group(1) in ref2fp:
        new = re.sub(r'\(property "Footprint" "[^"]*"',
                     '(property "Footprint" "%s"' % ref2fp[m.group(1)],
                     blk, count=1)
        if new != blk:
            changed += 1
        blk = new
    out.append(text[i:k])
    out.append(blk)
    i = j + 1

open(SCH, "w", encoding="utf-8").write("".join(out))
print("updated footprint fields:", changed)

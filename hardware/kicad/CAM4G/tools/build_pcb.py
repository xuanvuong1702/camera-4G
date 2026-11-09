import re
import os
import math
import pcbnew

ROOT = r"C:\Users\vuong\Documents\deepseek-harness\default-workspace\4g-camera\hardware\kicad\CAM4G"
NET = os.path.join(ROOT, "CAM4G.net")
OUT = os.path.join(ROOT, "CAM4G.kicad_pcb")
FPDIR = r"C:\Users\vuong\AppData\Local\Programs\KiCad\10.0\share\kicad\footprints"
CORE_FP = os.path.join(ROOT, "libs", "Core1106-PCB.pretty")

MM = pcbnew.FromMM
V = pcbnew.VECTOR2I


# ---------- netlist parser ----------
def tokenize(s):
    return re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', s)


def parse(tokens):
    it = iter(tokens)
    out = []
    stack = [out]
    for tok in it:
        if tok == '(':
            new = []
            stack[-1].append(new)
            stack.append(new)
        elif tok == ')':
            stack.pop()
        else:
            if tok.startswith('"'):
                tok = tok[1:-1]
            stack[-1].append(tok)
    return out[0]


text = open(NET, encoding="utf-8").read()
tree = parse(tokenize(text))


def find(node, key):
    for x in node:
        if isinstance(x, list) and x and x[0] == key:
            yield x


comps = {}
for c in find(tree, 'components'):
    for comp in find(c, 'comp'):
        ref = None
        for x in comp:
            if isinstance(x, list) and x and x[0] == 'ref':
                ref = x[1]
        if ref:
            comps[ref] = {}

nets = {}
for n in find(tree, 'nets'):
    for net in find(n, 'net'):
        name = None
        for x in net:
            if isinstance(x, list) and x and x[0] == 'name':
                name = x[1]
        if not name:
            continue
        for node in find(net, 'node'):
            r = p = None
            for x in node:
                if isinstance(x, list) and x and x[0] == 'ref':
                    r = x[1]
                if isinstance(x, list) and x and x[0] == 'pin':
                    p = x[1]
            if r and p:
                nets.setdefault(r, {})[p] = name

# ---------- footprint map ----------
FP = {
    "U1": ("CORE", "Core1106-SMT"),
    "U2": ("CUSTOM", "VQFN20_3.5"),
    "U3": ("Package_SON", "Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm"),
    "U4": ("Package_SO", "MSOP-10_3x3mm_P0.5mm"),
    "U5": ("Package_SO", "SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.3mm"),
    "U6": ("Package_SO", "TSSOP-20_4.4x6.5mm_P0.65mm"),
    "J1": ("Connector_USB", "USB_C_Receptacle_HRO_TYPE-C-31-M-12"),
    "J2": ("Connector_JST", "JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical"),
    "J3": ("Connector_FFC-FPC", "Hirose_FH12-20S-0.5SH_1x20-1MP_P0.50mm_Horizontal"),
    "J4": ("Connector_Card", "microSD_HC_Hirose_DM3AT-SF-PEJM5"),
    "J6": ("Connector_JST", "JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical"),
    "J7": ("Connector_JST", "JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical"),
    "J8": ("Connector_JST", "JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical"),
    "J9": ("Connector_JST", "JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical"),
    "J10": ("Connector_JST", "JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical"),
    "J11": ("Connector_PinHeader_1.27mm", "PinHeader_2x06_P1.27mm_Vertical"),
    "J12": ("Connector_PinHeader_2.54mm", "PinHeader_1x03_P2.54mm_Vertical"),
    "J13": ("Connector_PinHeader_2.54mm", "PinHeader_1x04_P2.54mm_Vertical"),
    "SW1": ("Button_Switch_SMD", "SW_SPST_B3S-1000"),
    "BT1": ("Battery", "Battery_Panasonic_CR1220-VCN_Vertical_CircularHoles"),
    "Q1": ("Package_TO_SOT_SMD", "SOT-23"),
    "Q2": ("Package_TO_SOT_SMD", "SOT-23"),
    "Q3": ("Package_TO_SOT_SMD", "SOT-23"),
    "D1": ("LED_SMD", "LED_0603_1608Metric"),
    "D2": ("LED_SMD", "LED_0603_1608Metric"),
    "D3": ("LED_SMD", "LED_0603_1608Metric"),
    "D5": ("Diode_SMD", "D_SOD-323"),
    "D6": ("Diode_SMD", "D_SOD-323"),
    "L1": ("Inductor_SMD", "L_Bourns-SRN8040_8x8.15mm"),
    "L2": ("Inductor_SMD", "L_Bourns-SRN4018"),
    "R7": ("Resistor_SMD", "R_1206_3216Metric"),
    "TP1": ("TestPoint", "TestPoint_Pad_1.5x1.5mm"),
    "TP2": ("TestPoint", "TestPoint_Pad_1.5x1.5mm"),
}
for r in comps:
    if r.startswith("R") and r not in FP:
        FP[r] = ("Resistor_SMD", "R_0603_1608Metric")
    if r.startswith("C") and r not in FP:
        FP[r] = ("Capacitor_SMD", "C_0603_1608Metric")
    if r == "NTC1":
        FP[r] = ("Resistor_SMD", "R_0603_1608Metric")

# ---------- board ----------
board = pcbnew.BOARD()
board.SetCopperLayerCount(4)
ds = board.GetDesignSettings()
ds.SetBoardThickness(MM(1.525))
ds.m_MinClearance = MM(0.15)
try:
    nc = ds.GetDefaultNetclass()
    nc.SetClearance(MM(0.15))
    ds.m_CopperEdgeClearance = MM(0.3)
except Exception as e:
    print('netclass', e)
ds.m_TrackMinWidth = MM(0.2)
ds.m_ViasMinSize = MM(0.6)
ds.m_ViasMinDrill = MM(0.3)

W, H = 100.0, 70.0


def edge(x1, y1, x2, y2):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(V(MM(x1), MM(y1)))
    s.SetEnd(V(MM(x2), MM(y2)))
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(MM(0.15))
    board.Add(s)


edge(0, 0, W, 0)
edge(W, 0, W, H)
edge(W, H, 0, H)
edge(0, H, 0, 0)

# mounting holes as board cutouts
for (mx, my) in [(12, 5), (W - 5, 5), (5, H - 5), (W - 5, H - 5)]:
    c = pcbnew.PCB_SHAPE(board)
    c.SetShape(pcbnew.SHAPE_T_CIRCLE)
    c.SetCenter(V(MM(mx), MM(my)))
    c.SetEnd(V(MM(mx + 1.6), MM(my)))
    c.SetLayer(pcbnew.Edge_Cuts)
    c.SetWidth(MM(0.15))
    board.Add(c)

# nets
netitems = {}
for r, pmap in nets.items():
    for p, name in pmap.items():
        if name not in netitems:
            ni = pcbnew.NETINFO_ITEM(board, name)
            board.Add(ni)
            netitems[name] = ni


# ---------- custom VQFN-20 3.5x3.5 ----------
def make_vqfn():
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference("U2")
    fp.SetValue("TPS61088")
    # pads 0.28 x 0.8, pitch 0.5, body 3.5
    pitch = 0.5
    padw, padh = 0.24, 0.6
    cx = 0.0
    # left side pins 1-5 top to bottom: y from -1 to +1
    num = 1
    for i in range(5):
        y = -1.0 + i * pitch
        pad = pcbnew.PAD(fp)
        pad.SetShape(pcbnew.PAD_SHAPE_RECT)
        pad.SetSize(V(MM(padh), MM(padw)))
        pad.SetPosition(V(MM(-1.525), MM(y)))
        pad.SetLayerSet(pcbnew.LSET.AllCuMask())
        pad.SetNumber(str(num))
        fp.Add(pad)
        num += 1
    for i in range(5):
        x = -1.0 + i * pitch
        pad = pcbnew.PAD(fp)
        pad.SetShape(pcbnew.PAD_SHAPE_RECT)
        pad.SetSize(V(MM(padw), MM(padh)))
        pad.SetPosition(V(MM(x), MM(1.525)))
        pad.SetLayerSet(pcbnew.LSET.AllCuMask())
        pad.SetNumber(str(num))
        fp.Add(pad)
        num += 1
    for i in range(5):
        y = 1.0 - i * pitch
        pad = pcbnew.PAD(fp)
        pad.SetShape(pcbnew.PAD_SHAPE_RECT)
        pad.SetSize(V(MM(padh), MM(padw)))
        pad.SetPosition(V(MM(1.525), MM(y)))
        pad.SetLayerSet(pcbnew.LSET.AllCuMask())
        pad.SetNumber(str(num))
        fp.Add(pad)
        num += 1
    for i in range(5):
        x = 1.0 - i * pitch
        pad = pcbnew.PAD(fp)
        pad.SetShape(pcbnew.PAD_SHAPE_RECT)
        pad.SetSize(V(MM(padw), MM(padh)))
        pad.SetPosition(V(MM(x), MM(-1.525)))
        pad.SetLayerSet(pcbnew.LSET.AllCuMask())
        pad.SetNumber(str(num))
        fp.Add(pad)
        num += 1
    ep = pcbnew.PAD(fp)
    ep.SetShape(pcbnew.PAD_SHAPE_RECT)
    ep.SetSize(V(MM(2.05), MM(2.05)))
    ep.SetPosition(V(0, 0))
    ep.SetLayerSet(pcbnew.LSET.AllCuMask())
    ep.SetNumber("21")
    fp.Add(ep)
    for pad in fp.Pads():
        pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        ls = pcbnew.LSET()
        ls.AddLayer(pcbnew.F_Cu)
        ls.AddLayer(pcbnew.F_Paste)
        ls.AddLayer(pcbnew.F_Mask)
        pad.SetLayerSet(ls)
    return fp


# ---------- placement ----------
placed_boxes = []
MARGIN = 1.5
ANCHOR = {
    "U2": (66, 55), "U3": (78, 55), "U5": (48, 61), "U4": (90, 45),
    "U6": (58, 15), "J11": (66, 38), "BT1": (68, 15),
}
GROUPS = {
    "U2": ["C1", "C2", "C3", "C6", "C7", "C9", "C4", "R1", "R2", "R3", "R4", "R5", "C5", "C8", "L1"],
    "U3": ["C10", "C11", "R6", "L2"],
    "U5": ["C13", "C14", "R10", "R13", "R11", "R12", "D1", "D2", "NTC1"],
    "U4": ["R7", "C12", "R8", "R9"],
    "U6": ["R25", "C17", "C18", "C19", "D5", "D6", "C16", "R31"],
    "J11": ["Q1", "Q2", "Q3", "R16", "R17", "R18", "R19", "R20"],
    "J1": ["R14", "R15", "R32", "R33", "R34", "R35"],
    "U1": ["R24", "R23", "C15", "R21", "D3", "TP1", "TP2"],
}


def load_fp(ref):
    lib, name = FP[ref]
    if lib == "CUSTOM":
        return make_vqfn()
    path = CORE_FP if lib == "CORE" else os.path.join(FPDIR, lib + ".pretty")
    fp = pcbnew.FootprintLoad(path, name)
    if fp is None:
        raise RuntimeError(f"missing footprint {lib}:{name} for {ref}")
    return fp


def pad_bbox(fp):
    k = 1e-6
    try:
        crt = fp.GetCourtyard(pcbnew.F_CrtYd)
        if crt is not None and not crt.IsEmpty():
            bb = crt.BBox()
            return bb.GetLeft() * k, bb.GetTop() * k, bb.GetRight() * k, bb.GetBottom() * k
    except Exception:
        pass
    l = t_ = 1e18
    r = b = -1e18
    for pad in fp.Pads():
        pb = pad.GetBoundingBox()
        l = min(l, pb.GetLeft())
        t_ = min(t_, pb.GetTop())
        r = max(r, pb.GetRight())
        b = max(b, pb.GetBottom())
    return l * k, t_ * k, r * k, b * k


def measure(ref, rot=0):
    fp = load_fp(ref)
    fp.SetOrientationDegrees(rot)
    l, t_, r, b = pad_bbox(fp)
    return fp, (r - l), (b - t_), (l + r) / 2, (t_ + b) / 2


def is_free(x, y, w, h, edge=False):
    for l, t_, r, b, _ in placed_boxes:
        if not (x + w / 2 + MARGIN < l or x - w / 2 - MARGIN > r or
                y + h / 2 + MARGIN < t_ or y - h / 2 - MARGIN > b):
            return False
    if not edge and (x - w / 2 < 1.0 or x + w / 2 > W - 1.0 or y - h / 2 < 1.0 or y + h / 2 > H - 1.0):
        return False
    return True


def place_center(ref, x, y, rot=0, edge=False):
    fp, w, h, ox, oy = measure(ref, rot)
    if not is_free(x, y, w, h, edge):
        return False
    fp.SetReference(ref)
    fp.SetPosition(V(MM(x - ox), MM(y - oy)))
    fp.SetOrientationDegrees(rot)
    board.Add(fp)
    for pad in fp.Pads():
        n = nets.get(ref, {}).get(pad.GetNumber())
        if n:
            pad.SetNet(netitems[n])
    l, t_, r, b = pad_bbox(fp)
    placed_boxes.append((l, t_, r, b, ref))
    return True


def find_spot(ref, rot, px, py, radius=20.0):
    fp, w, h, ox, oy = measure(ref, rot)
    best = None
    step = 1.27
    yy = 1.6
    while yy < H - 1.2:
        xx = 1.6
        while xx < W - 1.2:
            if is_free(xx, yy, w, h):
                d = math.hypot(xx - px, yy - py)
                if d <= radius and (best is None or d < best[0]):
                    best = (d, xx, yy)
            xx += step
        yy += step
    if best:
        return best[1], best[2]
    yy = 1.6
    while yy < H - 1.2:
        xx = 1.6
        while xx < W - 1.2:
            if is_free(xx, yy, w, h):
                return xx, yy
            xx += step
        yy += step
    return None, None


placed = set()

# 1. module (center)
for ref, x, y, r in [("U1", 30, 35, 0)]:
    if place_center(ref, x, y, r):
        placed.add(ref)

# 2. edge connectors
for ref, x, y, r in [("J3", 30, 6, 0), ("J1", 13, 62, 90), ("J2", 4, 17, 90),
                     ("J4", 88, 16, 0), ("J12", 92, 22, 0), ("J13", 92, 29, 0)]:
    if place_center(ref, x, y, r, edge=True):
        placed.add(ref)
    else:
        print("EDGE FAIL", ref)

# bottom row: place by measured width, left to right
x = 18.0
for ref in ["J6", "J7", "J8", "J9", "J10"]:
    fp, w, h, ox, oy = measure(ref, 0)
    if x + w > 78.0:
        print("bottom full", ref)
        continue
    if place_center(ref, x + w / 2, 65, 0, edge=True):
        placed.add(ref)
        x += w + 1.2

# 2b. preferred positions for critical parts
PREF = {"R5": (64.0, 51.5), "C8": (69.0, 51.5), "D6": (66.0, 11.0)}
for ref, (px, py) in PREF.items():
    if ref in comps and ref not in placed:
        xx, yy = find_spot(ref, 0, px, py, radius=5)
        if xx is not None and place_center(ref, xx, yy, 0):
            placed.add(ref)

# 3. anchors
for ref, (px, py) in ANCHOR.items():
    if ref not in comps:
        continue
    xx, yy = find_spot(ref, 0, px, py, radius=6)
    if xx is None:
        xx, yy = find_spot(ref, 0, px, py, radius=30)
    if xx is not None and place_center(ref, xx, yy, 0):
        placed.add(ref)

# 4. grouped passives
for anchor, kids in GROUPS.items():
    ax, ay = ANCHOR.get(anchor, (40, 30))
    for ref in kids:
        if ref in placed or ref not in comps:
            continue
        xx, yy = find_spot(ref, 0, ax, ay, radius=15)
        if xx is not None and place_center(ref, xx, yy, 0):
            placed.add(ref)

# 5. leftovers
for ref in comps:
    if ref in placed:
        continue
    xx, yy = find_spot(ref, 0, W/2, H/2, radius=90)
    if xx is not None and place_center(ref, xx, yy, 0):
        placed.add(ref)
    else:
        print("NO SPACE", ref)

print("placed", len(placed), "of", len(comps))
pcbnew.SaveBoard(OUT, board)
print("saved", OUT, "footprints", len(board.GetFootprints()), "nets", len(board.GetNetsByName()))






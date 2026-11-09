import re
import pcbnew

BASE = r"C:\Users\vuong\Documents\deepseek-harness\default-workspace\4g-camera\hardware\kicad\CAM4G"
PCB = BASE + r"\CAM4G.kicad_pcb"
SES = BASE + r"\CAM4G.ses"

MM = pcbnew.FromMM
V = pcbnew.VECTOR2I


def tokenize(s):
    return re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', s)


def parse(tokens):
    out = []
    stack = [out]
    for tok in tokens:
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


def children(node, key):
    return [x for x in node if isinstance(x, list) and x and x[0] == key]


text = open(SES, encoding="utf-8").read()
tree = parse(tokenize(text))

board = pcbnew.LoadBoard(PCB)

LAYERS = {
    "F.Cu": pcbnew.F_Cu,
    "B.Cu": pcbnew.B_Cu,
    "In1.Cu": pcbnew.In1_Cu,
    "In2.Cu": pcbnew.In2_Cu,
}

S = 1.0 / 10000.0


def to_mm(x, y):
    return float(x) * S, -float(y) * S


n_wires = 0
n_vias = 0

def find_all(node, key):
    res = []
    if isinstance(node, list):
        if node and node[0] == key:
            res.append(node)
        for x in node:
            res.extend(find_all(x, key))
    return res


netroots = find_all(tree, "network_out")
for netnode in (children(netroots[0], "net") if netroots else []):
    name = netnode[1]
    net = board.FindNet(name)
    if net is None:
        print("no net", name)
        continue
    for wire in children(netnode, "wire"):
        for path in children(wire, "path"):
            layer = LAYERS.get(path[1])
            width = float(path[2]) * S
            nums = [float(v) for v in path[3:] if not isinstance(v, list)]
            pts = [(nums[i], nums[i + 1]) for i in range(0, len(nums) - 1, 2)]
            for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                t = pcbnew.PCB_TRACK(board)
                t.SetStart(V(MM(to_mm(x1, y1)[0]), MM(to_mm(x1, y1)[1])))
                t.SetEnd(V(MM(to_mm(x2, y2)[0]), MM(to_mm(x2, y2)[1])))
                t.SetWidth(MM(width))
                t.SetLayer(layer)
                t.SetNet(net)
                board.Add(t)
                n_wires += 1
    for via in children(netnode, "via"):
        x, y = to_mm(via[2], via[3])
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(V(MM(x), MM(y)))
        v.SetWidth(MM(0.6))
        v.SetDrill(MM(0.3))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetNet(net)
        board.Add(v)
        n_vias += 1

# snap track endpoints to nearby via centers (rounding fix)
vias = [v for v in board.GetTracks() if v.Type() == pcbnew.PCB_VIA_T]


def near(pt):
    best = None
    for v in vias:
        d = ((v.GetPosition().x - pt.x) ** 2 + (v.GetPosition().y - pt.y) ** 2) ** 0.5
        if d < 0 and (best is None or d < best[0]):
            best = (d, v.GetPosition())
    return best


n_snap = 0
for tr in board.GetTracks():
    if tr.Type() != pcbnew.PCB_TRACE_T:
        continue
    for which in ("start", "end"):
        pt = tr.GetStart() if which == "start" else tr.GetEnd()
        nb = near(pt)
        if nb and nb[0] > 0:
            if which == "start":
                tr.SetStart(nb[1])
            else:
                tr.SetEnd(nb[1])
            n_snap += 1
print("snapped", n_snap)
pcbnew.SaveBoard(PCB, board)
print("tracks", n_wires, "vias", n_vias)

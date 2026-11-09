import pcbnew

BASE = r"C:\Users\vuong\Documents\deepseek-harness\default-workspace\4g-camera\hardware\kicad\CAM4G"
PCB = BASE + r"\CAM4G.kicad_pcb"
MM = pcbnew.FromMM
V = pcbnew.VECTOR2I

board = pcbnew.LoadBoard(PCB)


def add_via(netname, x, y):
    net = board.FindNet(netname)
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(V(MM(x), MM(y)))
    v.SetWidth(MM(0.45))
    v.SetDrill(MM(0.3))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetNet(net)
    board.Add(v)


def add_zone(netname, layer, rect, prio=0):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(board.FindNet(netname))
    z.SetLocalClearance(MM(0.15))
    z.SetMinThickness(MM(0.25))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    z.SetAssignedPriority(prio)
    o = z.Outline()
    o.NewOutline()
    for x, y in rect:
        o.Append(MM(x), MM(y))
    board.Add(z)


def courtyard(ref, size):
    for fp in board.GetFootprints():
        if fp.GetReference() != ref:
            continue
        if any(s.GetLayer() == pcbnew.F_CrtYd for s in fp.GraphicalItems()):
            continue
        pos = fp.GetPosition()
        r = pcbnew.PCB_SHAPE(fp)
        r.SetShape(pcbnew.SHAPE_T_RECT)
        r.SetLayer(pcbnew.F_CrtYd)
        r.SetWidth(MM(0.05))
        h = MM(size / 2)
        r.SetStart(V(pos.x - h, pos.y - h))
        r.SetEnd(V(pos.x + h, pos.y + h))
        fp.Add(r)


# VBAT vias at converter pins
for fp in board.GetFootprints():
    if fp.GetReference() == "U2":
        for pad in fp.Pads():
            if pad.GetNumber() == "9":
                p = pad.GetPosition()
                add_via("/VBAT", p.x / 1e6, p.y / 1e6)
    if fp.GetReference() == "C1":
        for pad in fp.Pads():
            if pad.GetNumber() == "1":
                p = pad.GetPosition()
                add_via("/VBAT", p.x / 1e6, p.y / 1e6)

full = [(1, 1), (99, 1), (99, 69), (1, 69)]
add_zone("/GND", pcbnew.In1_Cu, full)
add_zone("/VBAT", pcbnew.In2_Cu, full)
add_zone("/+5V_SYS", pcbnew.B_Cu, full, 0)
add_zone("/VBAT", pcbnew.B_Cu, [(58, 52), (72, 52), (72, 62), (58, 62)], 1)

courtyard("U2", 4.1)
courtyard("U3", 2.1)

pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(PCB, board)
print("post-route v2 done")

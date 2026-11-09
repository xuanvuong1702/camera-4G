import pcbnew

BASE = r"C:\Users\vuong\Documents\deepseek-harness\default-workspace\4g-camera\hardware\kicad\CAM4G"
PCB = BASE + r"\CAM4G.kicad_pcb"
MM = pcbnew.FromMM
V = pcbnew.VECTOR2I

board = pcbnew.LoadBoard(PCB)
net = board.FindNet("/VBAT")
if net is None:
    raise SystemExit("no VBAT net")


def pad_pos(ref, num):
    for fp in board.GetFootprints():
        if fp.GetReference() == ref:
            for pad in fp.Pads():
                if pad.GetNumber() == num:
                    return pad.GetPosition()
    return None


anchors = [pad_pos("U2", "9"), pad_pos("C1", "1")]
for pos in anchors:
    if pos is None:
        continue
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(pos)
    via.SetWidth(MM(0.45))
    via.SetDrill(MM(0.3))
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    via.SetNet(net)
    board.Add(via)

# F.Cu VBAT zone (full board)
z = pcbnew.ZONE(board)
z.SetLayer(pcbnew.F_Cu)
z.SetNet(net)
z.SetLocalClearance(MM(0.15))
z.SetMinThickness(MM(0.25))
z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
o = z.Outline()
o.NewOutline()
for x, y in [(1, 1), (99, 1), (99, 69), (1, 69)]:
    o.Append(MM(x), MM(y))
board.Add(z)

# B.Cu VBAT zone around the boost converter
z2 = pcbnew.ZONE(board)
z2.SetLayer(pcbnew.B_Cu)
z2.SetNet(net)
z2.SetLocalClearance(MM(0.15))
z2.SetMinThickness(MM(0.25))
z2.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
o2 = z2.Outline()
o2.NewOutline()
for x, y in [(58, 52), (72, 52), (72, 62), (58, 62)]:
    o2.Append(MM(x), MM(y))
board.Add(z2)

for zz in board.Zones():
    zz.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)

ds = board.GetDesignSettings()
for attr, val in [("m_ViasMinSize", 0.45), ("m_ViasMinDrill", 0.3),
                  ("m_TrackMinWidth", 0.15), ("m_MinClearance", 0.15)]:
    try:
        setattr(ds, attr, pcbnew.FromMM(val))
    except Exception as exc:
        print("skip", attr, exc)

pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(PCB, board)
print("post-route fix done")

import os

BASE = r"C:\Users\vuong\Documents\deepseek-harness\default-workspace\4g-camera\hardware\kicad\CAM4G"
OUT = os.path.join(BASE, "libs", "CAM4G.kicad_sym")

# (name, [(number, name, type), ...])
ICS = [
    ("TPS61088", [
        ("1", "VCC", "power_out"), ("2", "EN", "input"), ("3", "FSW", "input"),
        ("4", "SW", "passive"), ("5", "SW", "passive"), ("6", "SW", "passive"), ("7", "SW", "passive"),
        ("8", "BOOT", "passive"), ("9", "VIN", "power_in"), ("10", "SS", "passive"),
        ("11", "NC", "passive"), ("12", "NC", "passive"), ("13", "MODE", "input"),
        ("14", "VOUT", "passive"), ("15", "VOUT", "passive"), ("16", "VOUT", "passive"),
        ("17", "FB", "input"), ("18", "COMP", "passive"), ("19", "ILIM", "passive"),
        ("20", "AGND", "power_in"), ("21", "PGND", "power_in"),
    ]),
    ("TPS62840", [
        ("1", "GND", "power_in"), ("2", "VIN", "power_in"), ("3", "MODE", "input"),
        ("4", "EN", "input"), ("5", "VSET", "input"), ("6", "STOP", "input"),
        ("7", "SW", "passive"), ("8", "VOS", "input"), ("9", "EP", "power_in"),
    ]),
    ("INA226", [
        ("1", "A1", "input"), ("2", "A0", "input"), ("3", "ALERT", "output"),
        ("4", "SDA", "bidirectional"), ("5", "SCL", "input"), ("6", "VS", "power_in"),
        ("7", "GND", "power_in"), ("8", "VBUS", "input"), ("9", "IN-", "input"),
        ("10", "IN+", "input"),
    ]),
    ("CN3058E", [
        ("1", "TEMP", "input"), ("2", "ISET", "input"), ("3", "GND", "power_in"),
        ("4", "VIN", "power_in"), ("5", "BAT", "power_out"), ("6", "DONE", "output"),
        ("7", "CHRG", "output"), ("8", "FB", "input"), ("9", "EP", "power_in"),
    ]),
]


def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def make_symbol(name, pins):
    n = len(pins)
    nleft = (n + 1) // 2
    left = pins[:nleft]
    right = pins[nleft:]

    rows = max(len(left), len(right))
    height = max(rows * 2.54 + 5.08, 15.24)
    top = height / 2 - 2.54

    lines = []
    lines.append(f'\t(symbol "CAM4G:{name}"')
    lines.append('\t\t(exclude_from_sim no)')
    lines.append('\t\t(in_bom yes)')
    lines.append('\t\t(on_board yes)')
    lines.append(f'\t\t(property "Reference" "U" (at 0 {height/2 + 2.54:.2f} 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'\t\t(property "Value" "{name}" (at 0 {height/2 + 5.08:.2f} 0) (effects (font (size 1.27 1.27))))')
    lines.append('\t\t(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    lines.append('\t\t(property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    lines.append('\t\t(property "Description" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    lines.append(f'\t\t(symbol "{name}_0_1"')
    lines.append(f'\t\t\t(rectangle (start -10.16 {height/2:.2f}) (end 10.16 {-height/2:.2f})')
    lines.append('\t\t\t\t(stroke (width 0.254) (type default))')
    lines.append('\t\t\t\t(fill (type background))')
    lines.append('\t\t\t)')
    lines.append('\t\t)')
    lines.append(f'\t\t(symbol "{name}_1_1"')

    def pin(num, nm, typ, x, y, angle):
        return (f'\t\t\t(pin {typ} line (at {x:.2f} {y:.2f} {angle}) (length 5.08)\n'
                f'\t\t\t\t(name "{esc(nm)}" (effects (font (size 1.27 1.27))))\n'
                f'\t\t\t\t(number "{num}" (effects (font (size 1.27 1.27))))\n'
                f'\t\t\t)')

    for i, (num, nm, typ) in enumerate(left):
        y = top - i * 2.54
        lines.append(pin(num, nm, typ, -15.24, y, 0))
    for i, (num, nm, typ) in enumerate(right):
        y = top - i * 2.54
        lines.append(pin(num, nm, typ, 15.24, y, 180))

    lines.append('\t\t)')
    lines.append('\t)')
    return "\n".join(lines)


body = "\n".join(make_symbol(n, p) for n, p in ICS)
text = ('(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor") (generator_version "8.0")\n'
        + body + "\n)\n")

with open(OUT, "w", encoding="utf-8") as f:
    f.write(text)
print("written", OUT, len(text))

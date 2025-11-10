# pnml_parser.py
from dataclasses import dataclass
from typing import Dict, List
import xml.etree.ElementTree as ET

@dataclass(frozen=True)
class Place:
    id: str
    name: str
    initial: int

@dataclass(frozen=True)
class Transition:
    id: str
    name: str

@dataclass(frozen=True)
class Arc:
    id: str
    source: str
    target: str
    weight: int

@dataclass
class Net:
    places: Dict[str, Place]
    transitions: Dict[str, Transition]
    arcs: List[Arc]
    M0: Dict[str, int]

def _get_text(elem, path: str, default: str = "") -> str:
    node = elem.find(path)
    if node is None:
        return default
    return (node.text or "").strip()

def parse_pnml(path: str) -> Net:
    tree = ET.parse(path)
    root = tree.getroot()
    def tag_endswith(elem, name: str) -> bool: return elem.tag.endswith(name)

    net_elem = None
    for child in root.iter():
        if tag_endswith(child, "net"):
            net_elem = child; break
    if net_elem is None: raise ValueError("PNML missing <net> element")

    places, transitions, arcs = {}, {}, []

    for elem in net_elem.iter():
        if tag_endswith(elem, "place"):
            pid = elem.attrib.get("id"); 
            if not pid: raise ValueError("A <place> is missing an id")
            name = _get_text(elem, ".//{*}name/{*}text") or _get_text(elem, "name/text") or pid
            im = _get_text(elem, ".//{*}initialMarking/{*}text") or _get_text(elem, "initialMarking/text") or "0"
            initial = int(im.strip())
            if pid in places: raise ValueError(f"Duplicate place id: {pid}")
            places[pid] = Place(pid, name, initial)

        elif tag_endswith(elem, "transition"):
            tid = elem.attrib.get("id"); 
            if not tid: raise ValueError("A <transition> is missing an id")
            name = _get_text(elem, ".//{*}name/{*}text") or _get_text(elem, "name/text") or tid
            if tid in transitions: raise ValueError(f"Duplicate transition id: {tid}")
            transitions[tid] = Transition(tid, name)

        elif tag_endswith(elem, "arc"):
            aid = elem.attrib.get("id"); src = elem.attrib.get("source"); tgt = elem.attrib.get("target")
            if not (aid and src and tgt): raise ValueError("An <arc> is missing id/source/target")
            wtxt = _get_text(elem, ".//{*}inscription/{*}text") or _get_text(elem, "inscription/text") or "1"
            w = int(wtxt.strip())
            arcs.append(Arc(aid, src, tgt, w))

    all_ids = set(places.keys()) | set(transitions.keys())
    for a in arcs:
        if a.source not in all_ids: raise ValueError(f"Arc {a.id} source does not exist: {a.source}")
        if a.target not in all_ids: raise ValueError(f"Arc {a.id} target does not exist: {a.target}")

    M0 = {p: plc.initial for p, plc in places.items()}
    return Net(places, transitions, arcs, M0)

def summarize(net: Net) -> str:
    lines = []
    lines.append(f"Places ({len(net.places)}): " + ", ".join(sorted(net.places.keys())))
    lines.append(f"Transitions ({len(net.transitions)}): " + ", ".join(sorted(net.transitions.keys())))
    lines.append("Arcs ({0}): ".format(len(net.arcs)) + ", ".join(f"{a.source}->{a.target}[{a.weight}]" for a in net.arcs))
    lines.append("M0: " + ", ".join(f"{p}={net.M0[p]}" for p in sorted(net.places.keys())))
    return "\n".join(lines)

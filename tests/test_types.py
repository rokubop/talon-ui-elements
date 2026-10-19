import re
from pathlib import Path
from ..src.box_model import SELF_ALIGN_FRACTION
from ..src.core.animations import EASING_FUNCTIONS
from ..src.elements import element_collection
from ..src.fonts import _WEIGHT_ORDER
from ..src.nodes.node_svg import linecap, linejoin
from ..src.properties import ANCHORS, VALID_ELEMENT_PROP_TYPES
from ..src.utils import GRADIENT_DIRECTIONS
from ..src import value_types as vt
from .test_helpers import test_module, it


@test_module
class TypesTests:
    def test_types_match_code(self, done):
        """Each set's descriptions name the values of the table that does the work"""
        it("element names", expect=set(element_collection), actual=set(vt.ELEMENT))
        it("anchors", expect=set(ANCHORS), actual=set(vt.ANCHOR))
        it("anchors place by justify_self and align_self", expect=True,
           actual=all(j in vt.JUSTIFY_SELF and a in vt.ALIGN_SELF for j, a in ANCHORS.values()))
        it("self alignments", expect=set(SELF_ALIGN_FRACTION), actual=set(vt.JUSTIFY_SELF))
        it("transition easings", expect=set(EASING_FUNCTIONS), actual=set(vt.EASING))
        it("font weights", expect=set(_WEIGHT_ORDER), actual=set(vt.FONT_WEIGHT))
        it("linecaps", expect=set(linecap), actual=set(vt.STROKE_LINECAP))
        it("linejoins", expect=set(linejoin), actual=set(vt.STROKE_LINEJOIN))
        it("gradient directions", expect=set(GRADIENT_DIRECTIONS), actual=set(vt.GRADIENT_DIRECTION))

        types = vt.types()
        known = set(p for props in VALID_ELEMENT_PROP_TYPES.values() for p in props)
        it("every prop a set names is a real prop", expect=set(),
           actual={p for s in types.values() for p in s.get("props", [])} - known)
        it("every set described", expect=[],
           actual=[name for name, s in types.items() if not s["desc"]])
        source = (Path(__file__).parent.parent / "ui_elements.py").read_text(encoding="utf-8")
        it("every Type: link resolves", expect=[],
           actual=[f"{ns}.{name}" for ns, name in re.findall(r"Type: (\w+)\.(\w+)", source)
                   if ns != "ui_elements" or name not in types])
        done()

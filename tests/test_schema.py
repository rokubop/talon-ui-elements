import re
from pathlib import Path
from ..src.box_model import SELF_ALIGN_FRACTION
from ..src.core.animations import EASING_FUNCTIONS
from ..src.elements import element_collection
from ..src.fonts import _WEIGHT_ORDER
from ..src.nodes.node_svg import linecap, linejoin
from ..src.properties import ANCHORS, VALID_ELEMENT_PROP_TYPES
from ..src.utils import GRADIENT_DIRECTIONS
from .._schema import SCHEMA, ids
from .test_helpers import test_module, it


@test_module
class SchemaTests:
    def test_schema_matches_code(self, done):
        """schema.json and the tables the code keeps agree"""
        it("element names", expect=set(element_collection), actual=set(ids("element")))
        it("anchors", expect=set(ANCHORS), actual=set(ids("anchor")))
        it("anchors place by justify_self and align_self", expect=True,
           actual=all(j in ids("justify_self") and a in ids("align_self") for j, a in ANCHORS.values()))
        it("self alignments", expect=set(SELF_ALIGN_FRACTION), actual=set(ids("justify_self")))
        it("transition easings", expect=set(EASING_FUNCTIONS), actual=set(ids("easing")))
        it("font weights", expect=set(_WEIGHT_ORDER), actual=set(ids("font_weight")))
        it("linecaps", expect=set(linecap), actual=set(ids("stroke_linecap")))
        it("linejoins", expect=set(linejoin), actual=set(ids("stroke_linejoin")))
        it("gradient directions", expect=set(GRADIENT_DIRECTIONS), actual=set(ids("gradient_direction")))
        known = set(p for props in VALID_ELEMENT_PROP_TYPES.values() for p in props)
        it("every schema prop is a real prop", expect=set(),
           actual=set(SCHEMA["$defs"]["props"]["properties"]) - known)
        it("every set described", expect=[],
           actual=[name for name, d in SCHEMA["$defs"].items() if not d.get("description")])
        source = (Path(__file__).parent.parent / "ui_elements.py").read_text(encoding="utf-8")
        it("every Type: link resolves", expect=[],
           actual=[f"{ns}.{name}" for ns, name in re.findall(r"Type: (\w+)\.(\w+)", source)
                   if ns != "ui_elements" or name not in SCHEMA["$defs"]])
        done()

from talon import actions
from ..common import (
    code, example_with_code, interactive_section,
    build_controls_state, build_preview_props,
    INT, COLOR, BOOL,
)
from .. import theme as t
import textwrap

CONTROLS = [
    ("checked", BOOL, False),
    ("animated", BOOL, False),
    ("disabled", BOOL, False),
    ("size", INT, "22"),
    ("color", COLOR, ""),
    ("track_color", COLOR, ""),
    ("thumb_color", COLOR, ""),
]

def switch_stories():
    component, div, text, switch, state = actions.user.ui_elements([
        "component", "div", "text", "switch", "state"
    ])

    cs = build_controls_state(state, "sw", CONTROLS)
    preview_props = build_preview_props(CONTROLS, cs)
    preview_props["id"] = "sw_preview"
    preview_props["on_change"] = lambda e: cs["checked"][1](e.checked)

    return div(padding=32, gap=24)[
        text("Switch", font_size=22, font_weight="bold", color=t.TEXT),
        code(
            textwrap.dedent("""\
                switch = actions.user.ui_elements(['switch'])""")
        ),

        interactive_section(
            element_name="switch",
            preview_element=switch(**preview_props),
            controls_spec=CONTROLS,
            controls_state=cs,
            prefix="sw",
        ),

        # Examples
        div(gap=16)[
            text("Examples", font_size=18, font_weight="bold", color=t.TEXT, border_bottom=1, padding_bottom=12, border_color=t.BORDER),

            component(example_with_code, props={
                "title": "Sizes",
                "example": div(flex_direction="row", align_items="center", gap=16)[
                    switch(size=16),
                    switch(size=22),
                    switch(size=32),
                ],
                "code": textwrap.dedent("""\
                    switch(size=16)
                    switch(size=22)
                    switch(size=32)""")
            }),

            component(example_with_code, props={
                "title": "Custom Colors",
                "example": div(flex_direction="row", align_items="center", gap=16)[
                    switch(id="ex_green", color="4CAF50", checked=True),
                    switch(id="ex_red", color="F44336", checked=True),
                    switch(id="ex_purple", color="9C27B0", checked=True),
                ],
                "code": textwrap.dedent("""\
                    switch(color="4CAF50", checked=True)
                    switch(color="F44336", checked=True)
                    switch(color="9C27B0", checked=True)""")
            }),

            component(example_with_code, props={
                "title": "With Label (for_id)",
                "example": div(
                    flex_direction="row",
                    align_items="center",
                    gap=8,
                )[
                    switch(id="ex_label"),
                    text("Enable feature", for_id="ex_label", color=t.TEXT)
                ],
                "code": textwrap.dedent("""\
                    switch(id="a"),
                    text("Enable feature", for_id="a")""")
            }),

            component(example_with_code, props={
                "title": "Animated",
                "example": div(flex_direction="row", align_items="center", gap=16)[
                    switch(id="ex_anim1", animated=True),
                    switch(id="ex_anim2", animated=True, size=32),
                    switch(id="ex_anim3", animated=True, color="4CAF50", checked=True),
                ],
                "code": textwrap.dedent("""\
                    switch(animated=True)
                    switch(animated=True, size=32)
                    switch(animated=True, color="4CAF50")""")
            }),
        ],
    ]

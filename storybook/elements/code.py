from talon import actions
from ..common import code, example_with_code
from .. import theme as t
import textwrap

PYTHON_EXAMPLE = textwrap.dedent("""\
    from talon import Module, actions

    mod = Module()

    @mod.action_class
    class Actions:
        def hello(name: str = "world"):
            \"\"\"Say hello\"\"\"
            print(f"Hello {name}!")
            return True""")

TALON_EXAMPLE = textwrap.dedent("""\
    tag: user.ui_elements_hints_active
    mode: command
    -
    say hello: user.hello("world")
    volume <number>: user.set_volume(number)
    key(escape): user.close_ui()""")

def code_stories():
    component, div, text, state = actions.user.ui_elements([
        "component", "div", "text", "state"
    ])
    code_el = actions.user.ui_elements("code")

    return div(padding=32, gap=24)[
        text("Code", font_size=22, font_weight="bold", color=t.TEXT),
        code(
            textwrap.dedent("""\
                code = actions.user.ui_elements(['code'])""")
        ),

        # Examples
        div(gap=16)[
            text("Examples", font_size=18, font_weight="bold", color=t.TEXT, border_bottom=1, padding_bottom=12, border_color=t.BORDER),

            component(example_with_code, props={
                "title": "Python (default)",
                "example": div(background_color=t.BG_CODE, border_radius=8, padding=16)[
                    code_el(PYTHON_EXAMPLE),
                ],
                "code": textwrap.dedent("""\
                    code(\"\"\"\\
                        from talon import Module, actions

                        @mod.action_class
                        class Actions:
                            def hello(name: str = "world"):
                                print(f"Hello {name}!")
                    \"\"\")""")
            }),

            component(example_with_code, props={
                "title": "Talon",
                "example": div(background_color=t.BG_CODE, border_radius=8, padding=16)[
                    code_el(TALON_EXAMPLE, language="talon"),
                ],
                "code": textwrap.dedent("""\
                    code(\"\"\"\\
                        tag: user.ui_elements_hints_active
                        mode: command
                        -
                        say hello: user.hello("world")
                    \"\"\", language="talon")""")
            }),

            component(example_with_code, props={
                "title": "Selectable (drag to select, Ctrl+C to copy)",
                "example": div(background_color=t.BG_CODE, border_radius=8, padding=16)[
                    code_el(
                        'name = "world"\nresult = len(name)\nprint(f"length: {result}")',
                        selectable=True,
                    ),
                ],
                "code": textwrap.dedent("""\
                    code(
                        'name = "world"\\nresult = len(name)',
                        selectable=True,
                    )""")
            }),

            # Themes
            text("Themes", font_size=18, font_weight="bold", color=t.TEXT, border_bottom=1, padding_bottom=12, border_color=t.BORDER, margin_top=16),
            text("Built-in: monokai (default), vscode_dark, dracula, one_dark, github_light", font_size=13, color=t.TEXT_MUTED),

            component(theme_comparison),

            # Custom theme
            text("Custom Themes", font_size=18, font_weight="bold", color=t.TEXT, border_bottom=1, padding_bottom=12, border_color=t.BORDER, margin_top=16),

            component(example_with_code, props={
                "title": "Inline Custom Theme (dict)",
                "example": div(background_color=t.BG_CODE, border_radius=8, padding=16)[
                    code_el(
                        'def greet(name: str):\n    # say hello\n    return f"Hi {name}!"',
                        theme={
                            "keyword": "FF6B6B",
                            "function": "4ECDC4",
                            "string": "FFE66D",
                            "comment": "95ADB6",
                            "text": "F7FFF7",
                            "decorator": "4ECDC4",
                            "builtin": "4ECDC4",
                            "number": "FFE66D",
                            "operator": "FF6B6B",
                            "punctuation": "F7FFF7",
                            "constant": "FFE66D",
                        },
                    ),
                ],
                "code": textwrap.dedent("""\
                    code(
                        'def greet(name: str): ...',
                        theme={
                            "keyword": "FF6B6B",
                            "function": "4ECDC4",
                            "string": "FFE66D",
                            "comment": "95ADB6",
                            "text": "F7FFF7",
                            ...
                        },
                    )""")
            }),

            component(example_with_code, props={
                "title": "Register a Reusable Theme (from another repo)",
                "example": div(background_color=t.BG_CODE, border_radius=8, padding=16)[
                    code_el(textwrap.dedent("""\
                        # In your package (runs at load time):
                        actions.user.ui_elements_register_code_theme("nord", {
                            "keyword": "81A1C1",
                            "string": "A3BE8C",
                            "comment": "616E88",
                            "number": "B48EAD",
                            "function": "88C0D0",
                            "text": "D8DEE9",
                        })

                        # Then anyone can use it:
                        code("x = 42", theme="nord")""")),
                ],
                "code": textwrap.dedent("""\
                    actions.user.ui_elements_register_code_theme("nord", {
                        "keyword": "81A1C1",
                        "string": "A3BE8C",
                        "comment": "616E88",
                        ...
                    })

                    code("x = 42", theme="nord")""")
            }),

            # Custom language
            text("Custom Languages", font_size=18, font_weight="bold", color=t.TEXT, border_bottom=1, padding_bottom=12, border_color=t.BORDER, margin_top=16),

            component(example_with_code, props={
                "title": "Register a Custom Language (from another repo)",
                "example": div(background_color=t.BG_CODE, border_radius=8, padding=16)[
                    code_el(textwrap.dedent("""\
                        import re

                        # In your package (runs at load time):
                        actions.user.ui_elements_register_code_language("json", [
                            ("string", re.compile(r'"(?:[^"\\\\\\\\]|\\\\\\\\.)*"')),
                            ("number", re.compile(r'-?\\b\\d+(?:\\.\\d+)?\\b')),
                            ("keyword", re.compile(r'\\b(?:true|false|null)\\b')),
                            ("punctuation", re.compile(r'[{}\\[\\]:,]')),
                        ])

                        # Then anyone can use it:
                        code('{"name": "value", "count": 42}', language="json")""")),
                ],
                "code": textwrap.dedent("""\
                    import re

                    actions.user.ui_elements_register_code_language("json", [
                        ("string", re.compile(r'"(?:[^"\\\\]|\\\\.)*"')),
                        ("number", re.compile(r'-?\\b\\d+(?:\\.\\d+)?\\b')),
                        ("keyword", re.compile(r'\\b(?:true|false|null)\\b')),
                        ("punctuation", re.compile(r'[{}\\[\\]:,]')),
                    ])

                    code('{"name": "value"}', language="json")""")
            }),
        ],
    ]

THEME_SAMPLE = textwrap.dedent("""\
    from talon import Module

    mod = Module()

    @mod.action_class
    class Actions:
        def hello(name: str = "world"):
            # greeting
            return f"Hi {name}!\"""")

def theme_comparison():
    div, text = actions.user.ui_elements(["div", "text"])
    code_el = actions.user.ui_elements("code")

    themes = [
        ("Monokai (default)", "monokai", t.BG_CODE),
        ("VS Code Dark+", "vscode_dark", t.BG_CODE),
        ("Dracula", "dracula", "#282A36"),
        ("One Dark", "one_dark", "#282C34"),
        ("GitHub Light", "github_light", "#FFFFFF"),
    ]

    return div(gap=16, flex_direction="row", flex_wrap=True)[
        *[div(gap=6)[
            text(name, font_size=14, color=t.TEXT_SECONDARY),
            div(background_color=bg, border_radius=8, padding=20, border_width=1, border_color=t.BORDER_SUBTLE)[
                code_el(THEME_SAMPLE, theme=theme_key, font_size=14),
            ],
        ] for name, theme_key, bg in themes],
    ]

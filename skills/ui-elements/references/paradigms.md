# Reactive State vs Decoration Layer

Two paradigms for updating UI. Choose based on whether the layout itself changes.

## Decoration Layer (Game Overlay / Real-Time HUD)

Layout renders once. Rapid updates go through `highlight`, `set_text`, and refs — these paint on top of existing elements without re-rendering or recalculating layout.

`highlight_style` defines what highlighting looks like on an element. `highlight()`/`unhighlight()` toggle that style on and off. `highlight_briefly()` flashes it.

```python
from talon import Module, actions, cron

mod = Module()

# --- UI definition (renders once) ---

key_style = {
    "padding": 8,
    "border_radius": 4,
    "background_color": "222222",
    "highlight_style": {"background_color": "87ceeb88"},
}

def game_hud():
    div, text, screen, effect = actions.user.ui_elements(
        ["div", "text", "screen", "effect"]
    )

    def on_mount():
        # Subscribe to rapid game input events
        game_events.register(on_game_event)
        apm_tracker.start()
        return lambda: (game_events.unregister(on_game_event), apm_tracker.stop())

    effect(on_mount, [])

    return screen(align_items="center")[
        div(flex_direction="row", gap=4, padding=8, background_color="11111199")[
            div(id="left", **key_style)[text("left")],
            div(id="right", **key_style)[text("right")],
            div(id="jump", **key_style)[text("jump")],
            div(id="dash", **key_style)[text("dash")],
            text("", id="apm", font_size=12, color="888888", margin_left=12),
            text("", id="noise", font_size=12, color="AAAAAA", margin_left=8),
        ]
    ]

# --- Event handlers (update decoration layer, no re-render) ---

def on_game_event(event):
    if event.action == "tap":
        actions.user.ui_elements_highlight_briefly(event.target)
    elif event.action == "hold":
        actions.user.ui_elements_highlight(event.target)
    elif event.action == "release":
        actions.user.ui_elements_unhighlight(event.target)

def on_noise_event(event):
    actions.user.ui_elements_set_text("noise", event.input)

def on_apm_update(apm_count):
    actions.user.ui_elements_set_text("apm", f"{apm_count} APM")

@mod.action_class
class Actions:
    def show_game_hud():
        """Show game HUD"""
        actions.user.ui_elements_show(game_hud)
    def hide_game_hud():
        """Hide game HUD"""
        actions.user.ui_elements_hide(game_hud)
```

Key points:
- Elements have `id` props so they can be targeted by `highlight()` and `set_text()`
- `highlight_style` is defined on the element — it controls what the highlight looks like
- Event handlers fire many times per second but never trigger a re-render
- `set_text` can only change text content, `highlight` can only change visual style — neither adds/removes/repositions elements

## Reactive State (Form / Wizard / Dashboard)

Layout changes in response to user interaction — elements appear, disappear, resize, or get added to lists. Use `state.use()` for reactive re-renders.

```python
from talon import actions

BG = "#1a1e2a"
BG_CARD = "#252b3e"
BG_INPUT = "#2c3348"
BLUE = "#4a9af5"
TEXT = "#e4e8f0"
TEXT_DIM = "#a0a8c0"

def settings_panel():
    (div, text, button, screen, state, input_text,
     select, checkbox) = actions.user.ui_elements(
        ["div", "text", "button", "screen", "state",
         "input_text", "select", "checkbox"]
    )

    tab, set_tab = state.use("tab", "general")
    notifications, set_notifications = state.use("notifications", True)
    theme, set_theme = state.use("theme", "dark")

    TABS = [("general", "General"), ("display", "Display")]

    def tab_bar():
        return div(flex_direction="row", gap=8, border_bottom=1)[
            *[button(
                label,
                on_click=lambda e, t=t: set_tab(t),
                background_color=BLUE if tab == t else "transparent",
                border_radius=4,
                padding=8,
            ) for t, label in TABS]
        ]

    def general_tab():
        return div(gap=16)[
            div(gap=4)[
                text("Name", font_size=12, color=TEXT_DIM),
                input_text(id="name_input", autofocus=True,
                           background_color=BG_INPUT, border_radius=4, width=250),
            ],
            div(flex_direction="row", align_items="center", gap=8)[
                checkbox(checked=notifications,
                         on_change=lambda e: set_notifications(e.value)),
                text("Enable notifications"),
            ],
        ]

    def display_tab():
        return div(gap=16)[
            div(gap=4)[
                text("Theme", font_size=12, color=TEXT_DIM),
                select(id="theme_select", options=["dark", "light", "system"],
                       value=theme, on_change=lambda e: set_theme(e.value)),
            ],
        ]

    return screen(justify_content="center", align_items="center")[
        div(background_color=BG, padding=24, border_radius=8, gap=16,
            width=400, draggable=True)[
            text("Settings", font_size=20, font_weight="bold"),
            tab_bar(),
            general_tab() if tab == "general" else display_tab(),
            button("Save", on_click=on_save, background_color=BLUE,
                   border_radius=6, padding=12, width="100%"),
        ]
    ]
```

Key points:
- `state.use()` returns a value and setter — changing it re-renders the UI
- Conditional rendering (`if tab == "general"`) swaps entire sections in/out
- Form inputs (`input_text`, `select`, `checkbox`) use `on_change` handlers
- Re-renders are fine here — interactions are human-speed button clicks

## When to Mix Both

Some UIs need both. A dashboard might use state for tab navigation (layout changes) but decoration layer for a live status indicator (just color/text changes). Use state for structural changes, decoration layer for cosmetic ones.

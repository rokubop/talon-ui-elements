# 🔢 Dual Counters Tutorial

Build interactive numeric controls and trackers. Perfect for timers, score keeping, quantity adjustments, and any numeric input needs!

## What You'll Build

A pair of interactive counters with increment/decrement buttons, direct voice control, and real-time updates.

## What You'll Learn

- Creating interactive numeric controls
- Button-based value manipulation
- Voice-controlled numeric input
- State synchronization between multiple elements
- Building reusable counter components

## Step 1: Basic Single Counter

Let's start with one simple counter. Create `dual_counters.py`:

```python
from talon import actions

def dual_counters_ui():
    div, screen, text, button, state = actions.user.ui_elements(["div", "screen", "text", "button", "state"])

    count, set_count = state.use("count", 0)

    def increment():
        set_count(count + 1)

    def decrement():
        set_count(count - 1)

    return screen(justify_content="center", align_items="center")[
        div(
            background_color="333333",
            padding=24,
            border_radius=8,
            gap=16
        )[
            text("Counter", color="FFFFFF", font_size=20, text_align="center"),

            div(flex_direction="row", align_items="center", gap=16)[
                button(
                    "−",
                    background_color="FF6B6B",
                    color="FFFFFF",
                    padding=12,
                    border_radius=4,
                    font_size=20,
                    on_click=decrement,
                    min_width=40
                ),
                text(str(count), color="FFFFFF", font_size=24, text_align="center", min_width=50),
                button(
                    "+",
                    background_color="4ECDC4",
                    color="FFFFFF",
                    padding=12,
                    border_radius=4,
                    font_size=20,
                    on_click=increment,
                    min_width=40
                )
            ]
        ]
    ]
```

**What's happening?**

- `state.use("count", 0)` creates reactive state starting at 0
- `increment()` and `decrement()` functions update the count
- Buttons are styled with different colors (red for minus, teal for plus)
- `min_width` ensures consistent button and text sizing

## Step 2: Create a Reusable Counter Component

Let's make it reusable so we can have multiple counters:

```python
from talon import actions

def counter_component(label, state_key, initial_value=0):
    div, text, button, state = actions.user.ui_elements(["div", "text", "button", "state"])

    count, set_count = state.use(state_key, initial_value)

    def increment():
        set_count(count + 1)

    def decrement():
        set_count(count - 1)

    def reset():
        set_count(initial_value)

    return div(
        background_color="444444",
        padding=16,
        border_radius=8,
        gap=12,
        min_width=200
    )[
        text(label, color="FFFFFF", font_size=16, text_align="center", font_weight="bold"),

        div(flex_direction="row", align_items="center", justify_content="center", gap=12)[
            button(
                "−",
                background_color="FF6B6B",
                color="FFFFFF",
                padding=8,
                border_radius=4,
                font_size=18,
                on_click=decrement,
                min_width=35
            ),
            text(
                str(count),
                color="FFFFFF",
                font_size=28,
                text_align="center",
                min_width=60,
                font_weight="bold"
            ),
            button(
                "+",
                background_color="4ECDC4",
                color="FFFFFF",
                padding=8,
                border_radius=4,
                font_size=18,
                on_click=increment,
                min_width=35
            )
        ],

        button(
            "Reset",
            background_color="555555",
            color="FFFFFF",
            padding=6,
            border_radius=4,
            font_size=12,
            on_click=reset,
            width="100%"
        )
    ]

def dual_counters_ui():
    div, screen = actions.user.ui_elements(["div", "screen"])

    return screen(justify_content="center", align_items="center")[
        div(
            background_color="333333",
            padding=24,
            border_radius=8,
            gap=20
        )[
            text("Dual Counters", color="FFFFFF", font_size=24, text_align="center", margin_bottom=8),

            div(flex_direction="row", gap=20)[
                counter_component("Counter A", "counter_a", 0),
                counter_component("Counter B", "counter_b", 0)
            ]
        ]
    ]
```

**What's new?**

- `counter_component()` is a reusable function that creates a complete counter
- Each counter has its own state key (`counter_a`, `counter_b`)
- Added reset buttons to return to initial values
- Used `flex_direction="row"` to put counters side by side

## Step 3: Add Voice Control Functions

Let's add voice commands to control the counters:

```python
from talon import Module, actions

mod = Module()

# ... (include counter_component and dual_counters_ui from Step 2) ...

@mod.action_class
class Actions:
    def show_dual_counters():
        """Show dual counters interface"""
        actions.user.ui_elements_show(dual_counters_ui)

    def hide_dual_counters():
        """Hide dual counters interface"""
        actions.user.ui_elements_hide_all()

    def increment_counter_a():
        """Increment counter A"""
        current = actions.user.ui_elements_get_state("counter_a", 0)
        actions.user.ui_elements_set_state("counter_a", current + 1)

    def decrement_counter_a():
        """Decrement counter A"""
        current = actions.user.ui_elements_get_state("counter_a", 0)
        actions.user.ui_elements_set_state("counter_a", current - 1)

    def increment_counter_b():
        """Increment counter B"""
        current = actions.user.ui_elements_get_state("counter_b", 0)
        actions.user.ui_elements_set_state("counter_b", current + 1)

    def decrement_counter_b():
        """Decrement counter B"""
        current = actions.user.ui_elements_get_state("counter_b", 0)
        actions.user.ui_elements_set_state("counter_b", current - 1)

    def set_counter_value(counter: str, value: int):
        """Set a counter to a specific value"""
        if counter.lower() in ["a", "first", "left"]:
            actions.user.ui_elements_set_state("counter_a", value)
        elif counter.lower() in ["b", "second", "right"]:
            actions.user.ui_elements_set_state("counter_b", value)

    def reset_counters():
        """Reset both counters to zero"""
        actions.user.ui_elements_set_state("counter_a", 0)
        actions.user.ui_elements_set_state("counter_b", 0)

    def get_counter_total():
        """Get the sum of both counters"""
        a = actions.user.ui_elements_get_state("counter_a", 0)
        b = actions.user.ui_elements_get_state("counter_b", 0)
        return a + b
```

Create `dual_counters.talon`:

```talon
show counters: user.show_dual_counters()
hide counters: user.hide_dual_counters()

# Individual counter control
counter a up: user.increment_counter_a()
counter a down: user.decrement_counter_a()
counter b up: user.increment_counter_b()
counter b down: user.decrement_counter_b()

# Set specific values
set counter <user.text> to <number>: user.set_counter_value(text, number)

# Utility commands
reset counters: user.reset_counters()
total counters:
    total = user.get_counter_total()
    user.ui_elements_set_text("total_display", "Total: {total}")
```

## Step 4: Add Advanced Features

Let's add some sophisticated features like limits, step sizes, and a total display:

```python
def advanced_counter_component(label, state_key, initial_value=0, min_value=None, max_value=None, step=1):
    div, text, button, state = actions.user.ui_elements(["div", "text", "button", "state"])

    count, set_count = state.use(state_key, initial_value)

    def increment():
        new_value = count + step
        if max_value is None or new_value <= max_value:
            set_count(new_value)

    def decrement():
        new_value = count - step
        if min_value is None or new_value >= min_value:
            set_count(new_value)

    def reset():
        set_count(initial_value)

    # Determine if buttons should be disabled
    can_increment = max_value is None or count < max_value
    can_decrement = min_value is None or count > min_value

    return div(
        background_color="444444",
        padding=16,
        border_radius=8,
        gap=12,
        min_width=200
    )[
        text(label, color="FFFFFF", font_size=16, text_align="center", font_weight="bold"),

        # Show limits if they exist
        *([
            text(
                f"({min_value or '−∞'} to {max_value or '+∞'})",
                color="888888",
                font_size=12,
                text_align="center"
            )
        ] if min_value is not None or max_value is not None else []),

        div(flex_direction="row", align_items="center", justify_content="center", gap=12)[
            button(
                "−",
                background_color="FF6B6B" if can_decrement else "666666",
                color="FFFFFF" if can_decrement else "AAAAAA",
                padding=8,
                border_radius=4,
                font_size=18,
                on_click=decrement if can_decrement else None,
                min_width=35
            ),
            text(
                str(count),
                color="FFFFFF",
                font_size=28,
                text_align="center",
                min_width=60,
                font_weight="bold"
            ),
            button(
                "+",
                background_color="4ECDC4" if can_increment else "666666",
                color="FFFFFF" if can_increment else "AAAAAA",
                padding=8,
                border_radius=4,
                font_size=18,
                on_click=increment if can_increment else None,
                min_width=35
            )
        ],

        div(flex_direction="row", gap=8)[
            button(
                "Reset",
                background_color="555555",
                color="FFFFFF",
                padding=6,
                border_radius=4,
                font_size=12,
                on_click=reset,
                flex=1
            ),
            button(
                f"+{step}",
                background_color="666666",
                color="FFFFFF",
                padding=6,
                border_radius=4,
                font_size=12,
                on_click=increment if can_increment else None,
                flex=1
            )
        ]
    ]

def dual_counters_ui():
    div, screen, text, state = actions.user.ui_elements(["div", "screen", "text", "state"])

    # Get counter values for total calculation
    counter_a = state.get("score_home", 0)
    counter_b = state.get("score_away", 0)
    total = counter_a + counter_b

    return screen(justify_content="center", align_items="center")[
        div(
            draggable=True,
            background_color="333333",
            padding=24,
            border_radius=8,
            gap=20
        )[
            text("Score Keeper", color="FFFFFF", font_size=24, text_align="center", margin_bottom=8),

            div(flex_direction="row", gap=20)[
                advanced_counter_component("Home Team", "score_home", 0, 0, 99, 1),
                advanced_counter_component("Away Team", "score_away", 0, 0, 99, 1)
            ],

            # Total display
            div(
                background_color="555555",
                padding=12,
                border_radius=4,
                text_align="center"
            )[
                text("Total Points", color="CCCCCC", font_size=14),
                text(str(total), id="total_display", color="FFFFFF", font_size=20, font_weight="bold")
            ]
        ]
    ]
```

**What's new?**

- `min_value` and `max_value` parameters set limits
- `step` parameter controls increment size
- Buttons are visually disabled when limits are reached
- Added a total display that updates automatically
- Made it draggable with `draggable=True`

## Step 5: Add Practical Use Cases

Let's create some real-world examples:

```python
# Add to your Actions class:
def show_timer_controls():
    """Show timer minute and second controls"""

    def timer_ui():
        div, screen = actions.user.ui_elements(["div", "screen"])

        return screen(justify_content="center", align_items="center")[
            div(
                background_color="333333",
                padding=24,
                border_radius=8,
                gap=20
            )[
                text("Timer Setup", color="FFFFFF", font_size=24, text_align="center"),

                div(flex_direction="row", gap=20)[
                    advanced_counter_component("Minutes", "timer_minutes", 5, 0, 60, 1),
                    advanced_counter_component("Seconds", "timer_seconds", 0, 0, 59, 5)
                ]
            ]
        ]

    actions.user.ui_elements_show(timer_ui)

def show_quantity_adjuster():
    """Show quantity adjustment interface"""

    def quantity_ui():
        div, screen = actions.user.ui_elements(["div", "screen"])

        return screen(justify_content="center", align_items="center")[
            div(
                background_color="333333",
                padding=24,
                border_radius=8,
                gap=20
            )[
                text("Adjust Quantities", color="FFFFFF", font_size=24, text_align="center"),

                div(gap=16)[
                    advanced_counter_component("Small Items", "qty_small", 1, 1, 100, 1),
                    advanced_counter_component("Medium Items", "qty_medium", 1, 1, 50, 1),
                    advanced_counter_component("Large Items", "qty_large", 1, 1, 10, 1)
                ]
            ]
        ]

    actions.user.ui_elements_show(quantity_ui)

def show_score_tracker():
    """Show game score tracking interface"""
    actions.user.ui_elements_show(dual_counters_ui)  # Our main interface
```

Add to your `.talon` file:

```talon
show timer setup: user.show_timer_controls()
show quantities: user.show_quantity_adjuster()
show score tracker: user.show_score_tracker()

# Quick score updates
home team scores: user.increment_counter_a()
away team scores: user.increment_counter_b()
```

## 🎉 Outstanding Work!

You've built a complete numeric control system! Here's what you mastered:

- ✅ **Interactive numeric controls** - Buttons for increment/decrement
- ✅ **Reusable components** - Flexible counter building blocks
- ✅ **Constraint handling** - Min/max limits and step sizes
- ✅ **State management** - Multiple coordinated counters
- ✅ **Voice integration** - Direct numeric control via speech
- ✅ **Visual feedback** - Disabled states and limit displays
- ✅ **Real-world applications** - Timers, scores, quantities

## Real-World Applications

This pattern works great for:

- **Score keeping** - Sports games, competitions
- **Timer controls** - Pomodoro timers, cooking timers
- **Quantity adjusters** - Shopping carts, inventory
- **Settings panels** - Numeric configuration values
- **Progress tracking** - Goals, milestones, metrics
- **Game interfaces** - Lives, points, resources

## Advanced Challenges

Ready for more sophisticated features? Try these:

1. **Animation** - Smooth transitions when values change
2. **History tracking** - Undo/redo functionality
3. **Presets** - Save and load common value combinations
4. **Data export** - Save values to files or send to other apps
5. **Custom increments** - Different step sizes for different ranges
6. **Validation** - Custom rules beyond min/max
7. **Progress bars** - Visual representation of values relative to limits

## Next Tutorial

Ready for a complete dashboard? Try the **[Draggable HUD](draggable_hud.md)** tutorial to build a compact, information-rich interface with multiple components working together!

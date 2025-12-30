# 🎮 Game Key Overlay Tutorial

In this tutorial we will build a visual overlay showing game controls with arrow keys and action buttons that you can toggle on and off during gameplay.

![Game Keys Preview](../../examples/game_keys/game_keys_preview.png)

## Step 1: See full code
See [examples/game_keys_ui.py](../../examples/game_keys_ui.py) for the complete code.

Say "elements test" to see examples in action.

## The Big Picture

This example is organized into 4 functions:
- `key()` - Creates a labeled key button (like "jump", "dash")
- `key_icon()` - Creates a key with an icon (like arrow keys)
- `blank_key()` - Creates an invisible placeholder key for spacing
- `game_keys_ui()` - The main UI function that arranges all the keys

**Focus here first:** `game_keys_ui()` is the main UI function that gets called with `actions.user.ui_elements_show(game_keys_ui)`.

## Understanding the Structure

### Getting Elements
All UI elements come from `actions.user.ui_elements()`:

```python
screen, div, style = actions.user.ui_elements(["screen", "div", "style"])
```

The order of returned elements will match the order you specify in the list. See [elements.md](../elements.md) for a full list of available elements.

**Important:** `screen` is *usually* the first element - it's the root container that fills the entire screen. But you can also use `active_window` instead if you are playing in windowed mode.

### Reusable Functions
This example demonstrates creating reusable UI functions:

```python
def key(id, display: str):
    # Returns a key with text label

def key_icon(id, icon_name):
    # Returns a key with an icon
```

## Breaking Down game_keys_ui()

Let's look at the main function step by step:

### 1. The Screen Layout
```python
return screen(justify_content="flex_end")
```
- `screen` fills the entire display
- `flex_direction="column"` is the default, so content stacks vertically unless manually changed to `"row"`
- `justify_content="flex_end"` pushes content to the bottom since `flex_direction` is column
- `align_items` defaults to `"flex_start"`, so content aligns to the left

### 2. The Key Layout Structure
```python
div(flex_direction="row", margin_bottom=20, margin_left=20)[
    div()[  # Arrow keys section
        # Arrow key layout
    ],
    div()[  # Action keys section
        # Action key layout
    ],
]
```

This creates two main sections horizontally:
- Left section: Arrow keys
- Right section: Action keys
- `margin_bottom` and `margin_left` add spacing from the screen edges

### 3. Arrow Keys Section
```python
div()[
    div(flex_direction="row")[
        blank_key(), key_icon("up", "arrow_up"), blank_key()
    ],
    div(flex_direction="row")[
        key_icon("left", "arrow_left"), key_icon("down", "arrow_down"), key_icon("right", "arrow_right")
    ]
]
```

- `div()` arranges children vertically (`flex_direction="column"` is default)
- `div(flex_direction="row")` arranges children horizontally
- Uses `blank_key()` and `key_icon()` are custom functions which return ui_elements
- Each key is given a label and an id.
- Anything with an `id` can then be targeted by `actions.user.ui_elements_highlight`, `actions.user.ui_elements_unhighlight`, and `actions.user.ui_elements_highlight_briefly` for real-time feedback during gameplay

### 4. Action Keys Section
```python
div()[ # vertical children
    div(flex_direction="row")[ # horizontal children
        key("space", "jump"),
        key("lmb", "LMB"),
        key("rmb", "RMB"),
    ],
    div(flex_direction="row")[ # horizontal children
        key("q", "dash"),
        key("e", "heal"),
        key("shift", "sprint"),
    ]
]
```

- Arranges action keys in a 3x2 grid
- Each key shows a text label (like "jump", "dash")
- Uses `key()` for text-based keys

## Functions Explained

### key() Function
```python
def key(id, display: str):
    div, text = actions.user.ui_elements(["div", "text"])
    return div(class_name="key", id=id)[
        text(display)
    ]
```

- Takes an `id` for highlighting and `display` text
- Uses `class_name="key"` for consistent styling
- Returns a div containing text

### key_icon() Function
```python
def key_icon(id, icon_name):
    div, icon = actions.user.ui_elements(["div", "icon"])
    return div(class_name="key", id=id)[
        icon(icon_name, fill="FFFFFF", stroke="000000", stroke_width=3, size=30)
    ]
```

- Similar to `key()` but shows an icon instead of text
- Icons have white fill with black stroke for visibility
- Uses the same `.key` styling for consistency

### blank_key() Function
```python
def blank_key():
    div, text = actions.user.ui_elements(["div", "text"])
    return div(class_name="key", opacity=0.6)[text(" ")]
```

- Creates an invisible placeholder for layout spacing
- Uses lower opacity to make it barely visible
- Contains a space character to maintain proper sizing

## Styling with Classes

All keys use the `.key` class for consistent appearance:

```python
style({
    ".key": {
        "padding": 8,
        "background_color": "#33333366",
        "width": 60,
        "height": 60,
        "opacity": 0.8,
        "highlight_style": {
            "background_color": "#44BCE799",
        },
    }
})
```

- **Fixed dimensions**: `width: 60, height: 60` makes all keys the same size
- **Semi-transparent**: `background_color: "#33333366"` (the `66` at the end is alpha/transparency)
- **Centering**: `justify_content="center", align_items="center"` centers content in each key
- **Highlight effect**: `highlight_style` defines the color when highlighted

## Screen Positioning Options

The overlay is positioned at the bottom-left by default. Here are other positioning options:

- **Bottom right**: `flex_direction="row", justify_content="flex_end", align_items="flex_end"`
- **Top right**: `flex_direction="row", justify_content="flex_end", align_items="flex_start"`
- **Top left**: `flex_direction="row", justify_content="flex_start", align_items="flex_start"`
- **Bottom left**: `flex_direction="column", justify_content="flex_end", align_items="flex_start"` (current)

Use `margin` to offset from screen edges.

## Interactive Highlighting

Each key has a unique `id` for highlighting during gameplay:

```python
# Highlight a specific key
actions.user.ui_elements_highlight("up")

# Brief highlight (flashes then fades)
actions.user.ui_elements_highlight_briefly("space")

# Remove highlight
actions.user.ui_elements_unhighlight("up")
```

**Performance note**: Highlighting uses the decoration layer, which is faster than state updates for real-time feedback.

## Using Your Game Overlay

Show/hide the overlay with:
```python
actions.user.ui_elements_show(game_keys_ui)
actions.user.ui_elements_hide(game_keys_ui)
actions.user.ui_elements_toggle(game_keys_ui)
```

## Next Steps

- See [hello_world.md](../tutorials/hello_world.md) for setting up voice commands
- Learn about [Properties](../properties.md) for styling elements
- Understand [Components](../concepts/components.md) for reusable patterns
- Check [Rendering](../concepts/rendering.md) for highlight performance details
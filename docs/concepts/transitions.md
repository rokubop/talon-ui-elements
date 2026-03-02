# Transitions

Transitions smoothly animate property changes over time. The `transition` property defines which properties to animate and how long each animation takes.

## Basic Usage

```py
div(
    width=120,
    background_color="#4488FF",
    transition={
        "width": 400,                           # 400ms, default ease_out
        "background_color": 500,
        "opacity": (300, "linear"),             # 300ms with specific easing
        "border_radius": (500, "ease_out_bounce"),
    },
)
```

When a property value changes (via state change or re-render), the transition animates from the old value to the new value.

### Format

```py
transition={
    "property_name": duration_ms,
    "property_name": (duration_ms, "easing_function"),
    "all": 300,  # apply to all animatable properties
}
```

### Easing Functions

| Easing | Description |
|---|---|
| `"ease_out"` | Default. Starts fast, decelerates |
| `"ease_in"` | Starts slow, accelerates |
| `"ease_in_out"` | Slow start and end |
| `"linear"` | Constant speed |
| `"ease_in_cubic"` | Cubic acceleration |
| `"ease_out_bounce"` | Bounce effect at end |

### Animatable Properties

**Numeric:** `width`, `height`, `min_width`, `max_width`, `min_height`, `max_height`, `opacity`, `gap`, `font_size`, `border_width`, `top`, `bottom`, `left`, `right`

**Color:** `background_color`, `color`, `border_color`

**Other:** `border_radius`

## Highlight Transitions

When a node has both `highlight_style` and `transition`, hover highlights animate smoothly instead of snapping instantly:

```py
button(
    "Click me",
    highlight_style={"background_color": "#444444"},
    transition={"background_color": 150},
)
```

If an interactive node has `transition` with color properties but no explicit `highlight_style`, one is auto-generated from `highlight_color`:

```py
button("Click me", transition={"background_color": 150})
```

Works with style blocks too:

```py
style({
    ".btn": {
        "highlight_style": {
            "background_color": "#444444",
        },
        "transition": {
            "background_color": 150,
        },
    }
})
```

## Mount / Unmount Animations

Animate elements when they appear or disappear:

```py
div(
    opacity=1.0,
    top=0,
    position="relative",
    mount_style={"opacity": 0, "top": 20},
    unmount_style={"opacity": 0, "top": 20},
    transition={"opacity": 300, "top": 300},
)[
    text("I fade in and slide up!")
]
```

- `mount_style`: Starting values when the element first appears. Animates FROM these values TO the current property values.
- `unmount_style`: Target values when the element is removed. Animates FROM current values TO these values before removal.
- Both require `transition` to define timing.

## Retargeting

If a property changes mid-animation, the transition retargets smoothly from the current interpolated value to the new target. This applies to both property transitions and highlight transitions.

## Performance

- Transitions use a shared 16ms tick loop that only runs when animations are active.
- Highlight transitions only trigger decorator canvas redraws, not full re-renders.
- Nodes without `transition` have zero additional overhead.

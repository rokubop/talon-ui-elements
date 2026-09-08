# Window Focus

A ui_elements tree is not an OS window, so "the user clicked away" is not an
event we get for free. This is how it is detected, what it drives, and what to
turn on.

Try it: `elements examples` → **Window Focus**. The window reports what the
detector thinks, counts the times it lost focus, and lets you switch strategy
and opacity without a reload.

## Detecting focus loss

`user.ui_elements_focus_strategy` picks how it is detected. Every strategy
feeds the same decision, so they can be compared directly.

| Strategy | Signal | Catches | Misses |
| --- | --- | --- | --- |
| `canvas` | Talon's `Canvas.on_focused` on the decorator canvas | Anything that moves keyboard focus | Nothing, but fires spuriously - see below |
| `win_focus` | `ui.register("win_focus")`, matched on Talon's pid | Clicks into other apps, alt-tab, shortcuts | A click that focuses nothing at all |
| `click` | The global button poll behind `on_click_outside` | Presses landing outside every tree rect, even for a UI that never took OS focus | Alt-tab and other keyboard focus moves |
| `both` | `canvas` + `win_focus` | The default | |
| `all` | Every signal | | |
| `off` | Nothing | The tree is always treated as focused | |

Changing the setting takes hold at once - the passive sources stay attached
whatever the strategy is and are filtered when they fire, and the click poll,
the one source with a running cost, is attached and dropped to match.

A blur is never acted on the moment it arrives. It waits 120ms and is then
checked against the OS: if a Talon window is still active, the blur is dropped.
That is what makes the canvas signal usable - our own blockable canvases going
up and down look exactly like a blur followed by a focus, and the grace period
swallows the pair.

Reading and driving it:

```python
actions.user.ui_elements_window_focused()      # -> bool
actions.user.ui_elements_get_focus_strategy()  # -> str
actions.user.ui_elements_set_focus_strategy("click")   # None restores the setting
actions.user.ui_elements_focus_debug()         # prints the verdict and what each source says
```

Talon settings are read-only from Python, so the setters hold a runtime
override that beats the setting. Passing `None` hands it back.

To test the fade without waiting on detection:

```python
actions.user.ui_elements_force_unfocused()        # pin it unfocused
actions.user.ui_elements_release_forced_focus()   # back to the strategies
```

## Fading while unfocused

`user.ui_elements_unfocused_opacity` fades the whole tree while it does not
have focus. `1.0` (the default) leaves it alone; `0.5` makes it half
see-through. Values below `0.05` are clamped - a tree faded to nothing still
blocks the mouse where its canvases are, with nothing on screen to say so.

```talon
settings():
    user.ui_elements_unfocused_opacity = 0.6
```

```python
actions.user.ui_elements_set_unfocused_opacity(0.6)  # None restores the setting
actions.user.ui_elements_get_unfocused_opacity()
```

It is one group opacity over the finished canvas, not a per-element alpha, so
overlapping elements do not show through each other. The repaint re-blits the
layers already built - no layout, no component code.

## Keys without hints

Key and scroll bindings used to ride on `user.ui_elements_hints_active`, which
tied them to whether the UI was *labelled*. They are separate concerns: a UI
can want tab, escape and scroll while showing no hints at all.

| Tag | Active when | Covers |
| --- | --- | --- |
| `user.ui_elements_keys_active` | A tree is mounted | `tab`, `shift-tab`, arrows, `escape`, scroll commands, `ctrl -/=/0` scaling |
| `user.ui_elements_hints_active` | That tree is showing hints | The two-letter hint commands, `focus <hint>` |

So `show_hints=False` now keeps the keyboard working:

```python
actions.user.ui_elements_show(my_ui, show_hints=False)
```

Element-level key handling - typing into an input, space/enter on a focused
button, arrow keys in an open `select`, escape closing a modal - was never tied
to hints. It runs off the canvas key handler and needs only that the tree has
interactive elements, which is what gives its canvas keyboard focus.

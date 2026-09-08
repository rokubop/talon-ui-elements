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
override that beats the setting. Passing `None` hands it back. An override
lasts until it is cleared or Talon reloads; the settings are the persistent
way to configure this.

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

## Flattening to one colour

Fading alone does not help much with a dense UI: at any opacity you can see
through, the text is still there as texture. `user.ui_elements_unfocused_mask_color`
collapses the tree to a single colour while unfocused, keeping only its
silhouette.

**It is the on switch.** Strength and scope below do nothing while it is empty.
It defaults to `auto`, so this is on out of the box; set it to `""` to turn the
whole thing off. Text, borders and highlights all become the colour of the
background behind them and stop reading as detail, so a much lighter fade is
enough to see past it.

| Value | Effect |
| --- | --- |
| `"auto"` | Default. The tree's own background: its window background, else the outermost node under the root that paints one |
| `""` | Off. Colours are left alone. |
| a hex colour | That colour |

`user.ui_elements_unfocused_mask_strength` says how far the colour pulls. At
`1.0` nothing of the original survives and you get a flat shape. `0.25`, the
default, is a light tint over what is already drawn - enough to read as
inactive without losing the content.

`user.ui_elements_unfocused_mask_scope` says what it covers: `all` for the
whole tree, or `title_bar` to grey only the title bars the way an inactive OS
window does. A window built with `show_title_bar=False` has none, so `title_bar`
leaves it alone.

The defaults are `auto` at `0.25` over `all`, which reads as inactive without
losing the content. To turn it off:

```talon
settings():
    user.ui_elements_unfocused_mask_color = ""
```

```python
actions.user.ui_elements_set_unfocused_mask_color("auto")  # None restores the setting
actions.user.ui_elements_set_unfocused_mask_strength(0.25)
actions.user.ui_elements_set_unfocused_mask_scope("title_bar")
```

Flattening and fading are separate questions - how much detail is left, and how
much you can see through it - and separate passes. Neither needs the other.

## Going inert

`user.ui_elements_unfocused_inert` makes an unfocused tree stop responding, the
way an inactive OS window does:

- no hints, and the hints tag drops
- no hover highlighting
- a click anywhere but a title bar takes focus back instead of pressing what is
  under it, hints included if they were on

The title bar stays live throughout, so close, minimise and drag still work on
an unfocused window without waking it first.

On by default, paired with the flatten. A body drawn as one flat shape is
saying its inputs are dead, and it should be telling the truth. Clicking back in
also takes keyboard focus, so the tree is usable straight after the click that
woke it.

```talon
settings():
    user.ui_elements_unfocused_inert = false
```

Worth knowing for voice-first overlays: a hint can be spoken while another app
holds focus, but an inert tree draws no hints, so a HUD you read while working
in another window goes hint-less until you click it. Turn this off for those.

The decorator canvas is a separate layered window from the base, so anything it
paints - hints, highlights, the focus outline - flattens on its own and its
alpha stacks over the base. With `auto` the colours match and it reads as
slightly more solid in those spots.

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

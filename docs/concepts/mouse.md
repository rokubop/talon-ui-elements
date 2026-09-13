# Mouse

## Events come from the blockable canvas

ui_elements does not watch the mouse globally. Talon delivers mouse events to a canvas, so the UI builds **blockable canvases** shaped to its interactive area and listens on those.

That means:

- a press inside the UI arrives, and is consumed
- a press outside it never arrives at all
- text inputs get holes carved out of the blockable rects, so typing still reaches the OS

## Click outside is polled

A window with `minimize_on_click_outside`, `close_on_click_outside` or `on_click_outside` has to know about a press it will never be sent.

A full-screen canvas does not solve it:

- `blocks_mouse=False` receives no events at all
- `blocks_mouse=True` swallows the click before the app underneath sees it, which is wrong for an overlay sitting over a game

So the button state is polled instead. 16ms, only while a window asks for it, reading global coordinates so it works across every display.

The click is detected, never intercepted. Whatever is underneath still gets it. For a click that *is* consumed, use `modal` with `backdrop_click_close=True` - its backdrop is a real button, so the press stops there.

## Mouse rate

`user.ui_elements_mouse_rate` caps move events per second. Default 125, `0` to uncap.

A high polling rate mouse reports far faster than the display refreshes, and the surplus starves the canvas draw thread. Only applies to UIs with a blockable canvas, so a UI with nothing interactive is unaffected.

```talon
settings():
    user.ui_elements_mouse_rate = 125
```

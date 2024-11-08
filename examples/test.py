from talon import Module, actions, ui, cron
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.canvas import Canvas, MouseEvent
from talon.screen import Screen
from talon.skia import RoundRect, Surface, Paint
from talon.skia.util import color_from_sk, color_to_sk
from talon.types import Rect, Point2d
import time

mod = Module()
canvas = None
last_mouse_pos = None
rect_pos = Point2d(100, 100)

def get_screen(index: int = None) -> Screen:
    return ui.main_screen() if index is None else ui.screens()[index]

color = "red"
draw_busy = False
draw_busy_job = None

drag_start_pos = None
drag_relative_offset = None
drag_init_threshold = 4
drag_active = False

surface = Surface(500, 500)
surface_canvas = surface.canvas()

# paint.style = paint.Style.FILL
surface_canvas.paint.color = "white"
surface_canvas.draw_rect(Rect(0, 0, 500, 500))
snapshot_image = surface.snapshot()

def on_draw(c: SkiaCanvas):
    c.paint.color = color
    c.draw_rect(Rect(rect_pos.x, rect_pos.y, 100, 100))

    # c.draw_image(snapshot_image, 300, 300)
    # paint = Paint()
    # # paint.color = color_to_sk((255, 255, 255, 255))
    # surface.draw(c, 50, 50, surface_canvas.paint)

def on_mouse(e: MouseEvent):
    global last_mouse_pos, drag_relative_offset, drag_active, rect_pos, drag_start_pos

    if e.button == 0:
        if e.event == "mousedown" and not drag_relative_offset:
            drag_start_pos = e.gpos
            drag_relative_offset = Point2d(e.gpos.x - rect_pos.x, e.gpos.y - rect_pos.y)
        elif e.event == "mouseup":
            drag_active = False
            drag_start_pos = None
            drag_relative_offset = None

    if e.event == "mousemove" and drag_relative_offset:
        if not drag_active:
            if abs(e.gpos.x - drag_start_pos.x) > drag_init_threshold or abs(e.gpos.y - drag_start_pos.y) > drag_init_threshold:
                drag_active = True

        if drag_active and canvas:
            rect_pos.x = e.gpos.x - drag_relative_offset.x
            rect_pos.y = e.gpos.y - drag_relative_offset.y

            # canvas.move(10,10)
            refresh_drawing()

def draw_throttled():
    global draw_busy, draw_busy_job
    draw_busy = False
    if draw_busy_job:
        cron.cancel(draw_busy_job)
    draw_busy_job = None

def refresh_drawing():
    global draw_busy, draw_busy_job, canvas
    if canvas and not draw_busy:
        draw_busy = True
        # print(f"refreshing start {time.time()}")
        canvas.freeze()
        # print(f"refreshing end {time.time()}")
        draw_busy_job = cron.after("16ms", draw_throttled)


def freeze_drawing():
    global draw_busy, canvas
    if not draw_busy:
        canvas.freeze()

@mod.action_class
class Actions:
    def test_frog():
        """test frog"""
        global canvas, rect_pos

        if canvas:
            canvas.unregister("draw", on_draw)
            canvas.unregister("mouse", on_mouse)
            canvas.hide()
            canvas.close()
            canvas = None

        else:
            screen = get_screen()
            rect_pos = Point2d(100, 100)
            canvas = Canvas.from_screen(screen)

            # canvas = Canvas.from_rect(Rect(0, 0, 700, 700))
            # canvas.draggable = True
            canvas.blocks_mouse = True
            canvas.register("draw", on_draw)
            canvas.register("mouse", on_mouse)
            refresh_drawing()

    def test_frog_refresh():
        """test frog"""
        global canvas, color

        color = "blue" if color == "red" else "red"

        if canvas:
            canvas.freeze()
            canvas.show()

        # else:
        #     screen = get_screen()
        #     canvas = Canvas.from_screen(screen)
        #     canvas.register("draw", on_draw)
        #     canvas.freeze()
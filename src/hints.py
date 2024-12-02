from talon import Module, Context, cron
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.skia import RoundRect
from talon.types import Rect
from .state_manager import state_manager
from .interfaces import NodeType, ClickEvent
from .store import store
from .utils import safe_callback

mod = Module()
ctx = Context()
mod.tag("ui_elements_hints_active", desc="tag for ui elements")

class HintGenerator:
    def __init__(self):
        c_char = 99
        d_char = 100
        z_char = 123

        # Arbitrary decisions:
        # - Start buttons with 'b' and input_text with 'i'
        # - Second character start is based on personal
        #   preference for better recognition
        self.char_map = {
            "button": ("b", [chr(i) for i in range(c_char, z_char)]),
            "input_text": ("i", [chr(i) for i in range(d_char, z_char)])
        }

        # rather than using a generator, we increment char index
        self.state = {
            "button": 0,
            "input_text": 0
        }

    def generate_hint(self, node: NodeType):
        if node.id in store.id_to_hint:
            return store.id_to_hint[node.id]

        if node.element_type in self.char_map:
            first_char, second_char_list = self.char_map[node.element_type]
            index = self.state[node.element_type]
            if index < len(second_char_list):
                hint = f"{first_char}{second_char_list[index]}"
                self.state[node.element_type] += 1
                store.id_to_hint[node.id] = hint
                return hint
            else:
                print("Ran out of hint values while generating hints.")
                return ""

hint_generator = HintGenerator()

def trigger_hint_action(hint_trigger: str):
    for id, hint in store.id_to_hint.items():
        if hint == hint_trigger:
            node = store.id_to_node.get(id)
            if node:
                if node.element_type == "button":
                    state_manager.highlight_briefly(id)
                    # allow for a flash of the highlight before the click
                    cron.after("50ms", lambda: safe_callback(node.on_click, ClickEvent(id=id, cause="hint")))
                elif node.element_type == "input_text":
                    node.tree.focus_input(node.id)
            break

def draw_hint(c: SkiaCanvas, node: NodeType, text: str):
    c.paint.textsize = 12
    box_model = node.box_model.padding_rect
    hint_text_width = c.paint.measure_text(text)[1].width
    hint_text_height = c.paint.measure_text("X")[1].height
    hint_padding = 6
    hint_padding_width = hint_text_width + hint_padding
    hint_padding_height = hint_text_height + hint_padding
    hint_padding_rect = Rect(box_model.x - 10, box_model.y - 4, hint_padding_width, hint_padding_height)

    # border
    c.paint.color = node.options.color or "555555"
    c.paint.style = c.paint.Style.STROKE
    c.paint.stroke_width = 1
    c.draw_rrect(RoundRect.from_rect(hint_padding_rect, x=2, y=2))

    # background
    c.paint.color = node.options.background_color or "333333"
    c.paint.style = c.paint.Style.FILL
    c.draw_rrect(RoundRect.from_rect(hint_padding_rect, x=2, y=2))

    # text
    c.paint.color = node.options.color or "FFFFFF"
    c.paint.style = c.paint.Style.FILL
    c.draw_text(
        text,
        hint_padding_rect.x + hint_padding / 2,
        hint_padding_rect.y + hint_padding / 2 + hint_text_height
    )

def reset_hint_generator():
    global hint_generator
    hint_generator = HintGenerator()

def get_hint_generator():
    return hint_generator.generate_hint

def hint_tag_enable():
    ctx.tags = ["user.ui_elements_hints_active"]

def hint_tag_disable():
    ctx.tags = []

def hint_clear_state():
    store.id_to_hint.clear()
    reset_hint_generator()
    hint_tag_disable()

# TODO: can we make this so only currently shown hints
#  are captured instead of any two characters?
@mod.capture(rule="<user.letter> <user.letter>")
def ui_elements_hint_target(m) -> list[str]:
    return "".join(m.letter_list)

@mod.action_class
class Actions:
    def ui_elements_hint_action(ui_elements_hint_target: str):
        """Trigger hint action"""
        trigger_hint_action(ui_elements_hint_target)
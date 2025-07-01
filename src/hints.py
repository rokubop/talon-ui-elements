from talon import Module, Context, cron, settings, registry, actions
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.skia import RoundRect
from talon.types import Rect
from .core.state_manager import state_manager
from .core.store import store
from .interfaces import NodeType, ClickEvent
from .utils import safe_callback
from .versioning import talon_breaking_ui_version
from .core.entity_manager import entity_manager
from .interfaces import RenderTransforms

mod = Module()
ctx, ctx_hints_active_browser = Context(), Context()
mod.tag("ui_elements_hints_active", desc="tag for ui elements")

ctx_hints_active_browser.matches = """
tag: user.ui_elements_hints_active
and tag: browser
"""

first_time_setup = False

class HintGenerator:
    def __init__(self):
        a_ord = 97
        c_ord = 99
        d_ord = 100
        z_ord = 123

        # Arbitrary decisions:
        # - Start buttons with 'b', link with 'l', and input_text with 'i'
        # - Second character start is based on personal
        #   preference for better recognition
        b_char = settings.get("user.ui_elements_hints_button_first_char")
        i_char = settings.get("user.ui_elements_hints_input_text_first_char")
        l_char = settings.get("user.ui_elements_hints_link_first_char")
        self.char_map = {
            "button": (b_char, [chr(i) for i in range(c_ord, z_ord)]),
            "input_text": (i_char, [chr(i) for i in range(d_ord, z_ord)]),
            "link": (l_char, [chr(i) for i in range(a_ord, z_ord)])
        }

        # rather than using a generator, we increment char index
        self.state = {
            "button": (ord(b_char), 0),
            "input_text": (ord(i_char), 0),
            "link": (ord(l_char), 0)
        }

    def generate_hint(self, node: NodeType):
        if node.id in store.id_to_hint:
            return store.id_to_hint[node.id]

        if node.element_type in self.char_map:
            first_char, second_char_list = self.char_map[node.element_type]
            first_char_ascii, index = self.state[node.element_type]

            if index < len(second_char_list):
                # increment second char
                second_char = second_char_list[index]
                hint = f"{chr(first_char_ascii)}{second_char}"
                self.state[node.element_type] = (first_char_ascii, index + 1)
            else:
                # increment first char
                index = 0
                first_char_ascii += 1
                if first_char_ascii > ord("z"):
                    first_char_ascii = ord("a")
                second_char = second_char_list[index]
                hint = f"{chr(first_char_ascii)}{second_char}"
                self.state[node.element_type] = (first_char_ascii, index + 1)

            store.id_to_hint[node.id] = hint
            return hint

hint_generator = None

def trigger_hint_click(hint_trigger: str):
    for id, hint in store.id_to_hint.items():
        if hint == hint_trigger:
            node = store.id_to_node.get(id)
            if node:
                if node.element_type == "button" or node.element_type == "link":
                    state_manager.highlight_briefly(id)
                    # allow for a flash of the highlight before the click
                    cron.after("50ms", lambda: safe_callback(node.on_click, ClickEvent(id=id, cause="hint")))
                state_manager.focus_node(node)
            break

def trigger_hint_focus(hint_trigger: str):
    for id, hint in store.id_to_hint.items():
        if hint == hint_trigger:
            node = store.id_to_node.get(id)
            if node:
                state_manager.focus_node(node)
            break

def draw_hint(c: SkiaCanvas, node: NodeType, text: str, transforms: RenderTransforms = None):
    c.paint.textsize = settings.get("user.ui_elements_hints_size", 12)

    hint_text_width = c.paint.measure_text(text)[1].width
    hint_text_height = c.paint.measure_text("X")[1].height
    hint_padding = 6
    hint_padding_width = hint_text_width + hint_padding
    hint_padding_height = hint_text_height + hint_padding

    apply_clip = False
    clip_rect = None
    if node.box_model.is_visible() != True:
        apply_clip = True
        clip_rect = node.box_model.clip_rect

    if node.element_type == "button" or node.element_type == "link":
        box_model = node.box_model.content_rect
        offset_x = -hint_padding_width
        offset_y = -hint_padding_height
    else:
        box_model = node.box_model.padding_rect
        offset_x = -10
        offset_y = -4

    hint_padding_rect = Rect(
        box_model.x + offset_x,
        box_model.y + offset_y,
        hint_padding_width,
        hint_padding_height
    )

    if transforms and transforms.offset:
        hint_padding_rect.x += transforms.offset.x
        hint_padding_rect.y += transforms.offset.y

    if apply_clip:
        c.save()
        c.clip_rect(clip_rect)

    border_color = node.properties.border_color or "555555"
    background_color = node.properties.background_color or "333333"
    color = node.properties.color or "FFFFFF"

    if node.uses_decoration_render:
        border_color = node.resolve_render_property("border_color") or border_color
        background_color = node.resolve_render_property("background_color") or background_color
        color = node.resolve_render_property("color") or color

    if talon_breaking_ui_version() >= 2:
        c.paint.antialias = True

    # border
    c.paint.color = border_color
    c.paint.style = c.paint.Style.STROKE
    c.paint.stroke_width = 1
    c.draw_rrect(RoundRect.from_rect(hint_padding_rect, x=2, y=2))

    # background
    c.paint.color = background_color
    c.paint.style = c.paint.Style.FILL
    c.draw_rrect(RoundRect.from_rect(hint_padding_rect, x=2, y=2))

    # text
    c.paint.color = color
    c.paint.style = c.paint.Style.FILL
    c.draw_text(
        text,
        hint_padding_rect.x + hint_padding / 2,
        hint_padding_rect.y + hint_padding / 2 + hint_text_height
    )

    if apply_clip:
        c.restore()

def reset_hint_generator():
    global hint_generator
    hint_generator = HintGenerator()

def get_hint_generator():
    if not hint_generator:
        reset_hint_generator()
    return hint_generator.generate_hint

def rango_target(m) -> str:
    return m.rango_target

def init_rango_override():
    """
    If we have UI overlaying the screen with hints, then
    that should take priority over the rango hints in the browser.
    """
    if registry.captures.get("user.rango_target"):
        ctx_hints_active_browser.capture(
            "user.rango_target",
            rule="this is a workaround to make rango target match this really long sentence so that it doesnt match anything"
        )(rango_target)

def hint_tag_enable():
    global first_time_setup
    ctx.tags = ["user.ui_elements_hints_active"]
    if not first_time_setup:
        first_time_setup = True
        init_rango_override()

def hint_tag_disable():
    ctx.tags = []

class KeyPressOrRepeatHold:
    def __init__(self, action: callable):
        self.action = action
        self.repeat_job = None
        self.repeat_interval = "75ms"
        self.time_until_repeat_job = None
        self.time_until_repeat_interval = "370ms"

    def repeat(self):
        self.repeat_job = cron.interval(self.repeat_interval, self.action)

    def execute(self, key_down: bool):
        if key_down == None:
            self.cleanup()
            self.action()
        elif key_down == True:
            self.cleanup()
            self.action()
            self.time_until_repeat_job = cron.after(
                self.time_until_repeat_interval,
                self.repeat
            )
        elif key_down == False:
            self.cleanup()

    def cleanup(self):
        if self.time_until_repeat_job:
            cron.cancel(self.time_until_repeat_job)
            self.time_until_repeat_job = None
        if self.repeat_job:
            cron.cancel(self.repeat_job)
            self.repeat_job = None

focus_next = KeyPressOrRepeatHold(state_manager.focus_next)
focus_previous = KeyPressOrRepeatHold(state_manager.focus_previous)

def hint_clear_state():
    store.id_to_hint.clear()
    reset_hint_generator()
    hint_tag_disable()
    focus_next.cleanup()
    focus_previous.cleanup()

# TODO: can we make this so only currently shown hints
#  are captured instead of any two characters?
@mod.capture(rule="<user.letter> <user.letter>")
def ui_elements_hint_target(m) -> list[str]:
    return "".join(m.letter_list)

@mod.action_class
class Actions:
    def ui_elements_hint_action(action: str, ui_elements_hint_target: str = None):
        """Trigger ui_elements specific hint action"""
        if action == "click":
            if ui_elements_hint_target:
                trigger_hint_click(ui_elements_hint_target)
        elif action == "focus":
            if ui_elements_hint_target:
                trigger_hint_focus(ui_elements_hint_target)

    def ui_elements_key_action(action: str, key_down: bool = None):
        """Trigger ui_elements specific key action"""
        if action == "focus_next":
            focus_next.execute(key_down)
        elif action == "focus_previous":
            focus_previous.execute(key_down)
        elif action == "close":
            entity_manager.hide_all_trees()

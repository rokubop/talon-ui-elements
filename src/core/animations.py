import time
from dataclasses import dataclass
from talon import cron
from ..utils import hex_color


def linear(t):
    return t


def ease_in(t):
    return t * t


def ease_out(t):
    return 1 - (1 - t) * (1 - t)


def ease_in_out(t):
    return 2 * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2


def ease_in_cubic(t):
    return t * t * t


def ease_out_bounce(t):
    if t < 1 / 2.75:
        return 7.5625 * t * t
    elif t < 2 / 2.75:
        t -= 1.5 / 2.75
        return 7.5625 * t * t + 0.75
    elif t < 2.5 / 2.75:
        t -= 2.25 / 2.75
        return 7.5625 * t * t + 0.9375
    else:
        t -= 2.625 / 2.75
        return 7.5625 * t * t + 0.984375


EASING_FUNCTIONS = {
    "linear": linear,
    "ease_in": ease_in,
    "ease_out": ease_out,
    "ease_in_out": ease_in_out,
    "ease_in_cubic": ease_in_cubic,
    "ease_out_bounce": ease_out_bounce,
}

ANIMATABLE_NUMERIC_PROPERTIES = {
    "width",
    "height",
    "min_width",
    "max_width",
    "min_height",
    "max_height",
    "opacity",
    "gap",
    "font_size",
    "border_width",
    "top",
    "bottom",
    "left",
    "right",
}

ANIMATABLE_COLOR_PROPERTIES = {
    "background_color",
    "color",
    "border_color",
}

ANIMATABLE_PROPERTIES = ANIMATABLE_NUMERIC_PROPERTIES | ANIMATABLE_COLOR_PROPERTIES


@dataclass
class ActiveAnimation:
    property: str
    from_value: any
    to_value: any
    duration_ms: float
    easing: str
    start_time: float
    node_id: str


def interpolate_number(from_val, to_val, t):
    return from_val + (to_val - from_val) * t


def parse_hex_channels(hex_str):
    """Parse hex color string to (r, g, b, a) tuple of ints."""
    h = hex_str.lstrip("#")
    if len(h) == 6:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)
    elif len(h) == 8:
        return (
            int(h[0:2], 16),
            int(h[2:4], 16),
            int(h[4:6], 16),
            int(h[6:8], 16),
        )
    return None


def channels_to_hex(r, g, b, a=255):
    if a == 255:
        return f"{r:02X}{g:02X}{b:02X}"
    return f"{r:02X}{g:02X}{b:02X}{a:02X}"


def interpolate_color(from_hex, to_hex, t):
    from_ch = parse_hex_channels(from_hex)
    to_ch = parse_hex_channels(to_hex)
    if not from_ch or not to_ch:
        return to_hex if t >= 1 else from_hex
    r = max(0, min(255, int(interpolate_number(from_ch[0], to_ch[0], t))))
    g = max(0, min(255, int(interpolate_number(from_ch[1], to_ch[1], t))))
    b = max(0, min(255, int(interpolate_number(from_ch[2], to_ch[2], t))))
    a = max(0, min(255, int(interpolate_number(from_ch[3], to_ch[3], t))))
    return channels_to_hex(r, g, b, a)


class TransitionManager:
    def __init__(self, tree):
        self.tree = tree
        self.active = {}  # {node_id: {property: ActiveAnimation}}
        self.previous_values = {}  # {node_id: {property: value}}
        self.tick_job = None
        self._unmount_callback = None
        self._pending_mount_values = []
        self._mount_animations_pending = False
        self._last_tick_time = None

    def _parse_transition_config(self, transition_dict, property_name):
        """Parse transition config for a property. Returns (duration_ms, easing) or None."""
        config = transition_dict.get(property_name) or transition_dict.get("all")
        if config is None:
            return None
        if isinstance(config, (list, tuple)):
            duration_ms = config[0]
            easing = config[1] if len(config) > 1 else "ease_out"
        else:
            duration_ms = config
            easing = "ease_out"
        return (duration_ms, easing)

    def _get_animatable_value(self, node, prop):
        """Get a property value suitable for animation, or None if not animatable."""
        value = getattr(node.properties, prop, None)
        if value is None:
            return None
        if prop in ANIMATABLE_COLOR_PROPERTIES:
            if isinstance(value, str):
                return value
        elif prop in ANIMATABLE_NUMERIC_PROPERTIES:
            if isinstance(value, (int, float)):
                return value
        return None

    def _interpolate(self, anim, t):
        """Compute interpolated value for an animation at progress t."""
        easing_fn = EASING_FUNCTIONS.get(anim.easing, ease_out)
        eased_t = easing_fn(t)
        if anim.property in ANIMATABLE_COLOR_PROPERTIES:
            return interpolate_color(anim.from_value, anim.to_value, eased_t)
        return interpolate_number(anim.from_value, anim.to_value, eased_t)

    def _get_current_value(self, anim):
        """Get the current interpolated value of an active animation."""
        elapsed = (time.monotonic() - anim.start_time) * 1000
        t = min(1.0, elapsed / anim.duration_ms) if anim.duration_ms > 0 else 1.0
        return self._interpolate(anim, t)

    def _apply_value(self, node, prop, value):
        """Apply an interpolated value to a node property."""
        if prop == "opacity":
            node.properties.opacity = value
            node.properties.update_colors_with_opacity()
            self._cascade_opacity(node, value)
        else:
            setattr(node.properties, prop, value)

    def _cascade_opacity(self, node, opacity):
        """Cascade opacity to children that inherited it."""
        for child in node.get_children_nodes():
            if "opacity" in child.cascaded_properties:
                child.properties.opacity = opacity
                child.properties.update_colors_with_opacity()
                self._cascade_opacity(child, opacity)

    def detect_changes(self, node_id, node):
        """Compare new property values with stored previous values.
        Start animations for changed properties."""
        transition_dict = node.properties.transition
        if not transition_dict or not isinstance(transition_dict, dict):
            return

        if "all" in transition_dict:
            watch_props = ANIMATABLE_PROPERTIES
        else:
            watch_props = set(transition_dict.keys()) & ANIMATABLE_PROPERTIES

        # First encounter - snapshot values; start mount animations if mount_style exists
        if node_id not in self.previous_values:
            self.previous_values[node_id] = {}
            mount_style = getattr(node.properties, 'mount_style', None)

            for prop in watch_props:
                value = self._get_animatable_value(node, prop)
                if value is None:
                    continue

                # Check if this property should animate from mount_style
                if mount_style and prop in mount_style:
                    config = self._parse_transition_config(transition_dict, prop)
                    if config:
                        duration_ms, easing = config
                        from_value = mount_style[prop]
                        if prop in ANIMATABLE_COLOR_PROPERTIES and isinstance(from_value, str):
                            from_value = hex_color(from_value, property_name=prop)

                        anim = ActiveAnimation(
                            property=prop,
                            from_value=from_value,
                            to_value=value,
                            duration_ms=duration_ms,
                            easing=easing,
                            start_time=time.monotonic(),
                            node_id=node_id,
                        )
                        if node_id not in self.active:
                            self.active[node_id] = {}
                        self.active[node_id][prop] = anim
                        self.previous_values[node_id][prop] = value
                        # Defer applying mount values until after tree hierarchy is initialized
                        # to avoid corrupting inherited colors for children
                        self._pending_mount_values.append((node_id, prop, from_value))
                        continue

                self.previous_values[node_id][prop] = value

            return

        prev = self.previous_values[node_id]
        for prop in watch_props:
            new_value = self._get_animatable_value(node, prop)
            if new_value is None:
                continue

            old_value = prev.get(prop)
            if old_value is None:
                prev[prop] = new_value
                continue

            if old_value == new_value:
                continue

            config = self._parse_transition_config(transition_dict, prop)
            if not config:
                prev[prop] = new_value
                continue

            duration_ms, easing = config

            # Retarget from current interpolated position if animation is active
            from_value = old_value
            if node_id in self.active and prop in self.active[node_id]:
                from_value = self._get_current_value(self.active[node_id][prop])

            anim = ActiveAnimation(
                property=prop,
                from_value=from_value,
                to_value=new_value,
                duration_ms=duration_ms,
                easing=easing,
                start_time=time.monotonic(),
                node_id=node_id,
            )
            if node_id not in self.active:
                self.active[node_id] = {}
            self.active[node_id][prop] = anim

            # Update previous to target for next comparison
            prev[prop] = new_value
            # Set property to animation start value so first render shows it
            self._apply_value(node, prop, from_value)

        if self.active:
            self.start_tick_loop()

    def tick(self):
        """Called every 16ms. Interpolates values, applies to nodes, triggers repaint."""
        if not self.active or not self.tree:
            self.stop_tick_loop()
            if not self.active and self._unmount_callback:
                callback = self._unmount_callback
                self._unmount_callback = None
                callback()
            return

        if self.tree.destroying:
            self.stop_tick_loop()
            return

        now = time.monotonic()

        # Gap compensation: if the main thread was blocked (gap > 32ms),
        # push animation start_times forward so the animation pauses during
        # the gap instead of jumping. This keeps visual progression smooth.
        if self._last_tick_time is not None:
            gap_ms = (now - self._last_tick_time) * 1000
            if gap_ms > 32:
                adjustment = (gap_ms - 16) / 1000
                for node_id, animations in self.active.items():
                    for prop, anim in animations.items():
                        anim.start_time += adjustment
        self._last_tick_time = now

        finished_nodes = []
        is_unmounting = self._unmount_callback is not None
        phase = "UNMOUNT" if is_unmounting else "MOUNT"

        for node_id, animations in list(self.active.items()):
            node = self.tree.meta_state.id_to_node.get(node_id)
            if not node:
                finished_nodes.append(node_id)
                continue

            done_props = []
            has_opacity = "opacity" in animations

            # Apply non-opacity properties first
            for prop, anim in list(animations.items()):
                if prop == "opacity":
                    continue
                elapsed = (now - anim.start_time) * 1000
                t = (
                    min(1.0, elapsed / anim.duration_ms)
                    if anim.duration_ms > 0
                    else 1.0
                )
                value = self._interpolate(anim, t)
                self._apply_value(node, prop, value)
                if t >= 1.0:
                    done_props.append(prop)

            # Apply opacity last so update_colors_with_opacity sees final colors
            if has_opacity:
                anim = animations["opacity"]
                elapsed = (now - anim.start_time) * 1000
                t = (
                    min(1.0, elapsed / anim.duration_ms)
                    if anim.duration_ms > 0
                    else 1.0
                )
                value = self._interpolate(anim, t)
                self._apply_value(node, "opacity", value)
                if t >= 1.0:
                    done_props.append("opacity")

            for prop in done_props:
                del animations[prop]

            if not animations:
                finished_nodes.append(node_id)

        for node_id in finished_nodes:
            self.active.pop(node_id, None)

        # Trigger repaint
        if self.tree and not self.tree.destroying:
            self.tree.render_animation_frame()

        if not self.active:
            self.stop_tick_loop()
            if self._unmount_callback:
                callback = self._unmount_callback
                self._unmount_callback = None
                callback()

    def apply_pending_mount_values(self):
        """Apply mount animation starting values after tree hierarchy is fully initialized.
        This must be called after init_node_hierarchy so children have already
        inherited correct (non-modified) colors from parents."""
        if not self._pending_mount_values:
            return
        for node_id, prop, value in self._pending_mount_values:
            node = self.tree.meta_state.id_to_node.get(node_id)
            if node:
                self._apply_value(node, prop, value)
        self._pending_mount_values.clear()
        self._mount_animations_pending = True

    def start_mount_animations(self):
        """Start mount animations with fresh timing. Call after tree is fully rendered.
        Deferred via cron.after to let other pending tree renders complete first,
        preventing competing renders from blocking animation ticks."""
        if not self._mount_animations_pending:
            return
        self._mount_animations_pending = False

        def _deferred_start():
            if not self.tree or self.tree.destroying:
                return
            now = time.monotonic()
            for node_id, anims in self.active.items():
                for prop, anim in anims.items():
                    anim.start_time = now
            self._last_tick_time = None
            self.start_tick_loop()

        cron.after("0ms", _deferred_start)

    def start_unmount(self, on_complete):
        """Start exit animations for all nodes with unmount_style. Calls on_complete when done."""
        has_unmount_anim = False

        for node_id, node in list(self.tree.meta_state.id_to_node.items()):
            unmount_style = getattr(node.properties, 'unmount_style', None)
            transition_dict = node.properties.transition
            if not unmount_style or not transition_dict or not isinstance(transition_dict, dict):
                continue

            for prop, to_value in unmount_style.items():
                if prop not in ANIMATABLE_PROPERTIES:
                    continue
                config = self._parse_transition_config(transition_dict, prop)
                if not config:
                    continue

                duration_ms, easing = config
                from_value = self._get_animatable_value(node, prop)
                if from_value is None:
                    continue

                if prop in ANIMATABLE_COLOR_PROPERTIES and isinstance(to_value, str):
                    to_value = hex_color(to_value, property_name=prop)

                # Retarget from current interpolated position if animation is active
                if node_id in self.active and prop in self.active[node_id]:
                    from_value = self._get_current_value(self.active[node_id][prop])

                anim = ActiveAnimation(
                    property=prop,
                    from_value=from_value,
                    to_value=to_value,
                    duration_ms=duration_ms,
                    easing=easing,
                    start_time=time.monotonic(),
                    node_id=node_id,
                )
                if node_id not in self.active:
                    self.active[node_id] = {}
                self.active[node_id][prop] = anim
                has_unmount_anim = True

        if has_unmount_anim:
            self._unmount_callback = on_complete
            self._last_tick_time = None
            self.start_tick_loop()
        else:
            on_complete()

    def start_tick_loop(self):
        """Start the 16ms tick loop if not already running."""
        if not self.tick_job and self.active:
            self.tick_job = cron.interval("16ms", self.tick)

    def stop_tick_loop(self):
        """Cancel the tick loop when no active animations remain."""
        if self.tick_job:
            cron.cancel(self.tick_job)
            self.tick_job = None

    def clear_node(self, node_id):
        """Remove animation state for a destroyed node."""
        self.active.pop(node_id, None)
        self.previous_values.pop(node_id, None)

    def has_active_animations(self):
        return bool(self.active)

    def destroy(self):
        """Cleanup on tree destroy."""
        self.stop_tick_loop()
        self.active.clear()
        self.previous_values.clear()
        self._unmount_callback = None
        self._pending_mount_values.clear()
        self._mount_animations_pending = False
        self._last_tick_time = None
        self.tree = None

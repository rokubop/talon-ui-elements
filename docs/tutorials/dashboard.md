# 🧭 Dashboard Tutorial

Build a compact heads-up display (HUD) that combines multiple information sources into one draggable, always-available interface. Perfect for monitoring system status, tracking metrics, or creating a personal dashboard!

![Dashboard Preview](../../examples/dashboard_preview.png)

## Step 1: See full code
See [examples/dashboard_ui.py](../../examples/dashboard_ui.py) for the complete code.

Say "elements test" to see examples in action.

## Code Breakdown

**Draggable Interface**: The `draggable=True` property makes the entire dashboard moveable, perfect for positioning it anywhere on your screen during work sessions.

**Real-time Updates**: The dashboard uses `effect` hooks to automatically refresh time and system information every second, keeping data current without manual updates.

**Compact Layout**: Strategic use of `gap`, `padding`, and `min_width` creates an information-dense interface that doesn't waste screen space while remaining readable.

**Color Coding**: Different colors (`4ECDC4` for time, `CCCCCC` for secondary info) help users quickly scan and identify different types of information at a glance.

**Flexible Content**: The modular structure makes it easy to add new sections - just add more `div` blocks with your content. Each section can have different styling and update intervals.

**Semi-transparent Background**: The `333333EE` background with alpha transparency lets you see through the dashboard to content underneath while maintaining readability.

**Positioning Control**: Using `justify_content="flex_start"` and `align_items="flex_end"` places the dashboard in the bottom-left by default, but it can be dragged anywhere.

**Using the Function**: Import this function into your Talon voice commands and control visibility with `actions.user.ui_elements_show(dashboard_ui)`, `actions.user.ui_elements_hide(dashboard_ui)`, `actions.user.ui_elements_hide_all()`, or `actions.user.ui_elements_toggle(dashboard_ui)`.

## Step 2: Setting Up Interaction

Use the following for visibility
```python
actions.user.ui_elements_show(dashboard_ui)
actions.user.ui_elements_hide(dashboard_ui)
actions.user.ui_elements_hide_all()
actions.user.ui_elements_toggle(dashboard_ui)
```

For more information on setting up voice commands, see [hello_world.md](../tutorials/hello_world.md).

The dashboard automatically updates its time and system information every second using effect hooks.

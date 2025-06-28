# 🧭 Draggable HUD Tutorial

Build a compact heads-up display (HUD) that combines multiple information sources into one draggable, always-available interface. Perfect for monitoring system status, tracking metrics, or creating a personal dashboard!

## What You'll Build

A floating dashboard with system info, quick actions, and real-time updates that you can position anywhere on your screen.

## What You'll Learn

- Creating compact, information-dense interfaces
- Combining multiple data sources in one UI
- Building draggable, persistent overlays
- Real-time data updates and refreshing
- Efficient layout for small spaces

## Step 1: Basic HUD Structure

Let's start with a simple status display. Create `draggable_hud.py`:

```python
from talon import actions
import datetime

def draggable_hud_ui():
    div, screen, text, state = actions.user.ui_elements(["div", "screen", "text", "state"])

    # Get current time
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_date = now.strftime("%Y-%m-%d")

    return screen(
        justify_content="flex_start",
        align_items="flex_end"  # Position at bottom-left
    )[
        div(
            draggable=True,
            background_color="333333EE",  # Semi-transparent
            padding=12,
            border_radius=6,
            margin=16,
            gap=8,
            min_width=200
        )[
            text("HUD", color="FFFFFF", font_size=14, font_weight="bold", text_align="center"),

            div(gap=4)[
                text(current_time, color="4ECDC4", font_size=16, font_weight="bold"),
                text(current_date, color="CCCCCC", font_size=12)
            ]
        ]
    ]
```

**What's happening?**

- `justify_content="flex_start"` and `align_items="flex_end"` position at bottom-left
- `draggable=True` makes the entire HUD draggable
- Semi-transparent background (`333333EE`) so it doesn't block content underneath
- Current time and date display with different styling

## Step 2: Add System Information

Let's add more useful information:

```python
from talon import actions
import datetime
import psutil  # For system info - you might need to install this

def get_system_info():
    """Get current system information"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        return {
            "cpu": cpu_percent,
            "memory": memory_percent,
            "memory_gb": round(memory.used / (1024**3), 1)
        }
    except:
        return {"cpu": 0, "memory": 0, "memory_gb": 0}

def draggable_hud_ui():
    div, screen, text, state = actions.user.ui_elements(["div", "screen", "text", "state"])

    # Get current time
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_date = now.strftime("%Y-%m-%d")

    # Get system info
    sys_info = get_system_info()

    # Get refresh counter from state (for forcing updates)
    refresh_count = state.get("hud_refresh", 0)

    return screen(
        justify_content="flex_start",
        align_items="flex_end"
    )[
        div(
            draggable=True,
            background_color="333333EE",
            padding=12,
            border_radius=6,
            margin=16,
            gap=8,
            min_width=200
        )[
            text("System HUD", color="FFFFFF", font_size=14, font_weight="bold", text_align="center"),

            # Time section
            div(gap=4)[
                text(current_time, color="4ECDC4", font_size=16, font_weight="bold"),
                text(current_date, color="CCCCCC", font_size=12)
            ],

            # Divider
            div(height=1, background_color="666666", margin_top=4, margin_bottom=4),

            # System info section
            div(gap=4)[
                div(flex_direction="row", justify_content="space_between")[
                    text("CPU:", color="CCCCCC", font_size=12),
                    text(f"{sys_info['cpu']:.1f}%", color="FFB74D", font_size=12)
                ],
                div(flex_direction="row", justify_content="space_between")[
                    text("RAM:", color="CCCCCC", font_size=12),
                    text(f"{sys_info['memory']:.1f}%", color="FF8A65", font_size=12)
                ],
                div(flex_direction="row", justify_content="space_between")[
                    text("Used:", color="CCCCCC", font_size=12),
                    text(f"{sys_info['memory_gb']}GB", color="81C784", font_size=12)
                ]
            ]
        ]
    ]
```

**What's new?**

- `get_system_info()` gathers CPU and memory usage
- Two-column layout using `justify_content="space_between"`
- Different colors for different metrics
- Visual divider between sections

## Step 3: Add Quick Actions

Let's add some useful buttons for common tasks:

```python
from talon import actions
import datetime

# ... (include get_system_info from Step 2) ...

def quick_action_button(label, color, action):
    button = actions.user.ui_elements(["button"])[0]

    return button(
        label,
        background_color=color,
        color="FFFFFF",
        padding=6,
        border_radius=4,
        font_size=11,
        on_click=action,
        flex=1
    )

def draggable_hud_ui():
    div, screen, text, state = actions.user.ui_elements(["div", "screen", "text", "state"])

    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_date = now.strftime("%Y-%m-%d")

    sys_info = get_system_info()

    def refresh_hud():
        current = state.get("hud_refresh", 0)
        state.set("hud_refresh", current + 1)

    def hide_hud():
        actions.user.ui_elements_hide_all()

    def show_tasks():
        print("Opening task manager...")
        # You could open your todo list or other task interface here

    return screen(
        justify_content="flex_start",
        align_items="flex_end"
    )[
        div(
            draggable=True,
            background_color="333333EE",
            padding=12,
            border_radius=6,
            margin=16,
            gap=8,
            min_width=200
        )[
            text("System HUD", color="FFFFFF", font_size=14, font_weight="bold", text_align="center"),

            # Time section
            div(gap=4)[
                text(current_time, color="4ECDC4", font_size=16, font_weight="bold"),
                text(current_date, color="CCCCCC", font_size=12)
            ],

            # System info section
            div(gap=4)[
                div(flex_direction="row", justify_content="space_between")[
                    text("CPU:", color="CCCCCC", font_size=12),
                    text(f"{sys_info['cpu']:.1f}%", color="FFB74D", font_size=12)
                ],
                div(flex_direction="row", justify_content="space_between")[
                    text("RAM:", color="CCCCCC", font_size=12),
                    text(f"{sys_info['memory']:.1f}%", color="FF8A65", font_size=12)
                ]
            ],

            # Quick actions
            div(gap=6)[
                div(flex_direction="row", gap=6)[
                    quick_action_button("Refresh", "4CAF50", refresh_hud),
                    quick_action_button("Tasks", "2196F3", show_tasks)
                ],
                div(flex_direction="row", gap=6)[
                    quick_action_button("Hide", "666666", hide_hud)
                ]
            ]
        ]
    ]
```

**What's new?**

- `quick_action_button()` creates consistent small buttons
- `flex=1` makes buttons fill available space evenly
- `refresh_hud()` forces a UI update by changing state
- Multiple rows of action buttons

## Step 4: Add Auto-Refresh and More Data

Let's make it update automatically and add more useful information:

```python
from talon import Module, actions
import datetime

mod = Module()

def get_enhanced_system_info():
    """Get detailed system information"""
    try:
        import psutil
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        return {
            "cpu": cpu_percent,
            "memory": memory.percent,
            "memory_gb": round(memory.used / (1024**3), 1),
            "disk": disk.percent,
            "processes": len(psutil.pids())
        }
    except:
        return {
            "cpu": 0, "memory": 0, "memory_gb": 0,
            "disk": 0, "processes": 0
        }

def status_indicator(label, value, unit, color):
    div, text = actions.user.ui_elements(["div", "text"])

    return div(flex_direction="row", justify_content="space_between")[
        text(f"{label}:", color="CCCCCC", font_size=11),
        text(f"{value}{unit}", color=color, font_size=11, font_weight="bold")
    ]

def draggable_hud_ui():
    elements = ["div", "screen", "text", "state", "button", "effect"]
    div, screen, text, state, button, effect = actions.user.ui_elements(elements)

    # Auto-refresh every 2 seconds
    effect(
        lambda: actions.user.schedule_hud_refresh(),
        [],  # No dependencies - runs once
        cleanup=lambda: None
    )

    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_date = now.strftime("%Y-%m-%d")

    sys_info = get_enhanced_system_info()
    task_count = state.get("task_count", 0)

    def quick_action(label, color, action):
        return button(
            label,
            background_color=color,
            color="FFFFFF",
            padding=6,
            border_radius=4,
            font_size=10,
            on_click=action,
            flex=1
        )

    return screen(
        justify_content="flex_start",
        align_items="flex_end"
    )[
        div(
            draggable=True,
            background_color="333333F0",
            padding=12,
            border_radius=6,
            margin=16,
            gap=8,
            min_width=220,
            border="1px solid #555555"
        )[
            # Header
            div(flex_direction="row", justify_content="space_between", align_items="center")[
                text("HUD", color="FFFFFF", font_size=14, font_weight="bold"),
                text("●", color="4CAF50", font_size=12)  # Live indicator
            ],

            # Time section
            div(gap=2)[
                text(current_time, color="4ECDC4", font_size=16, font_weight="bold", text_align="center"),
                text(current_date, color="CCCCCC", font_size=11, text_align="center")
            ],

            # System metrics
            div(gap=3)[
                status_indicator("CPU", f"{sys_info['cpu']:.1f}", "%", "FFB74D"),
                status_indicator("RAM", f"{sys_info['memory']:.1f}", "%", "FF8A65"),
                status_indicator("Disk", f"{sys_info['disk']:.1f}", "%", "BA68C8"),
                status_indicator("Proc", sys_info['processes'], "", "81C784")
            ],

            # Tasks section
            div(gap=3)[
                div(height=1, background_color="666666"),
                status_indicator("Tasks", task_count, "", "4FC3F7")
            ],

            # Quick actions
            div(flex_direction="row", gap=4)[
                quick_action("↻", "4CAF50", lambda: actions.user.refresh_hud()),
                quick_action("✕", "666666", lambda: actions.user.ui_elements_hide_all())
            ]
        ]
    ]

@mod.action_class
class Actions:
    def show_draggable_hud():
        """Show the draggable HUD"""
        actions.user.ui_elements_show(draggable_hud_ui)

    def refresh_hud():
        """Force refresh the HUD"""
        # Trigger a re-render by updating state
        current = actions.user.ui_elements_get_state("hud_refresh", 0)
        actions.user.ui_elements_set_state("hud_refresh", current + 1)

    def schedule_hud_refresh():
        """Schedule automatic HUD refresh"""
        import threading
        import time

        def refresh_loop():
            time.sleep(2)  # Wait 2 seconds
            try:
                actions.user.refresh_hud()
                actions.user.schedule_hud_refresh()  # Schedule next refresh
            except:
                pass  # HUD might be closed

        thread = threading.Thread(target=refresh_loop)
        thread.daemon = True
        thread.start()

    def update_hud_task_count(count: int):
        """Update the task count displayed in HUD"""
        actions.user.ui_elements_set_state("task_count", count)
```

Create `draggable_hud.talon`:

```talon
show hud: user.show_draggable_hud()
hide hud: user.ui_elements_hide_all()
refresh hud: user.refresh_hud()

set task count <number>: user.update_hud_task_count(number)
```

**What's new?**

- `effect()` sets up auto-refresh on mount
- `status_indicator()` creates consistent metric displays
- Live indicator (green dot) shows the HUD is updating
- More compact button labels using symbols
- Automatic refresh scheduling with threading
- Border for better visual definition

## Step 5: Add Customization Options

Let's make the HUD customizable:

```python
# Add to your Actions class:
def toggle_hud_position():
    """Toggle HUD between corners"""
    current_position = actions.user.ui_elements_get_state("hud_position", "bottom-left")

    positions = ["bottom-left", "bottom-right", "top-left", "top-right"]
    current_index = positions.index(current_position)
    next_position = positions[(current_index + 1) % len(positions)]

    actions.user.ui_elements_set_state("hud_position", next_position)

def toggle_hud_size():
    """Toggle between compact and expanded view"""
    current_size = actions.user.ui_elements_get_state("hud_size", "normal")
    new_size = "compact" if current_size == "normal" else "normal"
    actions.user.ui_elements_set_state("hud_size", new_size)

# Update the draggable_hud_ui function to use these settings:
def draggable_hud_ui():
    elements = ["div", "screen", "text", "state", "button", "effect"]
    div, screen, text, state, button, effect = actions.user.ui_elements(elements)

    # Get position and size preferences
    position = state.get("hud_position", "bottom-left")
    size_mode = state.get("hud_size", "normal")

    # Calculate positioning
    justify_map = {
        "bottom-left": "flex_start", "top-left": "flex_start",
        "bottom-right": "flex_end", "top-right": "flex_end"
    }
    align_map = {
        "bottom-left": "flex_end", "bottom-right": "flex_end",
        "top-left": "flex_start", "top-right": "flex_start"
    }

    # ... rest of the UI logic with position-based styling ...

    return screen(
        justify_content=justify_map[position],
        align_items=align_map[position]
    )[
        div(
            draggable=True,
            background_color="333333F0",
            padding=12 if size_mode == "normal" else 8,
            border_radius=6,
            margin=16,
            gap=8 if size_mode == "normal" else 4,
            min_width=220 if size_mode == "normal" else 180,
            # ... rest of the div content ...
        )
    ]
```

Add to your `.talon` file:

```talon
move hud: user.toggle_hud_position()
toggle hud size: user.toggle_hud_size()
```

## 🎉 Incredible Achievement!

You've built a sophisticated, always-available dashboard! Here's everything you mastered:

- ✅ **Compact interface design** - Maximum info in minimal space
- ✅ **Real-time updates** - Live system monitoring
- ✅ **Draggable positioning** - User-controlled placement
- ✅ **Multiple data sources** - System metrics, time, custom data
- ✅ **Quick actions** - Convenient buttons for common tasks
- ✅ **Auto-refresh** - Hands-free data updates
- ✅ **Customization** - Position and size preferences

## Real-World Applications

This HUD pattern is perfect for:

- **Development monitoring** - Build status, test results, server health
- **System administration** - Resource usage, process monitoring
- **Productivity tracking** - Task counts, time tracking, goals
- **Gaming overlays** - Stats, timers, resource monitoring
- **Trading dashboards** - Market data, portfolio status
- **Home automation** - Device status, weather, alerts

## Advanced Challenges

Ready for expert-level features? Try these:

1. **Data persistence** - Save settings and preferences
2. **Multiple themes** - Dark, light, colorful options
3. **Plugin system** - Modules for different data sources
4. **Graphs and charts** - Visual data representation
5. **Alerts and notifications** - Threshold-based warnings
6. **Remote data** - API integration for external services
7. **Performance optimization** - Efficient updates for large datasets

## Integration Ideas

Connect your HUD to other tutorials:

- Show **todo list** task counts
- Display **counter** values from other UIs
- Integrate with **option selector** for quick choices
- Use **cheatsheet** data for context-aware help

## Conclusion

Congratulations! You've completed all the major UI Elements tutorials and learned to build:

- ✅ Basic interfaces and styling
- ✅ Interactive components and state management
- ✅ Dynamic, context-aware interfaces
- ✅ Complex forms and user input
- ✅ Dialog and confirmation systems
- ✅ Numeric controls and constraints
- ✅ Dashboard and monitoring interfaces

You now have all the skills needed to build any voice-activated UI you can imagine. The patterns you've learned can be combined and adapted for countless applications. Happy building! 🚀

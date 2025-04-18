from talon import actions

test_module_runners = {}
success = 0
failure = 0
total = 0

test_title_color = "1bd0f5"
error_message_color = "ff6b8e"

def run_tests():
    global success, failure, total
    success = 0
    failure = 0
    total = 0
    actions.user.ui_elements_set_state("log", [])
    for runner in test_module_runners.values():
        runner()
    log(f"Tests complete: {success} passed, {failure} failed")

def test_module(cls):
    def runner():
        instance = cls()
        if hasattr(instance, "run"):
            log(f"Running {cls.__name__}", color=test_title_color)
            instance.run()
        return instance

    test_module_runners[cls.__name__] = runner
    return cls

def test(test_name, expect, actual):
    global success, failure, total
    total += 1
    if expect == actual:
        success += 1
        log_success(test_name)
    else:
        failure += 1
        log_failure(test_name)
        log(f"     Expected {expect} but got actual {actual}", color=error_message_color)

def test_truthy(test_name, actual):
    global success, failure, total
    total += 1
    if actual:
        success += 1
        log_success(test_name)
    else:
        failure += 1
        log_failure(test_name)
        log(f"     Expected True but got False", color=error_message_color)

def log(message: str, color: str = "FFFFFF"):
    text = actions.user.ui_elements(["text"])
    result = text(message, font_size=14, color=color)
    actions.user.ui_elements_set_state("log", lambda log: log + [result])

def log_success(message: str):
    div, text, icon = actions.user.ui_elements(["div", "text", "icon"])

    result = div(flex_direction="row", gap=8, align_items="center")[
        icon("check", color="00FF00", size=14, stroke_width=6),
        text(message, font_size=14),
    ]

    actions.user.ui_elements_set_state("log", lambda log: log + [result])

def log_failure(message: str):
    div, text, icon = actions.user.ui_elements(["div", "text", "icon"])

    result = div(flex_direction="row", gap=8, align_items="center")[
        icon("close", color="ff0000", size=14, stroke_width=6),
        text(message, font_size=14),
    ]

    actions.user.ui_elements_set_state("log", lambda log: log + [result])
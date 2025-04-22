from talon import actions
from time import time

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
    pending = len(test_module_runners)

    def on_runner_done():
        nonlocal pending
        pending -= 1
        if pending == 0:
            log(f"Tests complete: {success} passed, {failure} failed")

    for runner in test_module_runners.values():
        runner(on_runner_done)

def test_module(cls):
    def runner(done_callback):
        instance = cls()
        log(f"Running {cls.__name__}", color=test_title_color)
        for attr in dir(instance):
            if attr.startswith("test_"):
                getattr(instance, attr)(done_callback)
        return instance

    test_module_runners[cls.__name__] = runner
    return cls

def it(test_name, expect, actual):
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

class Spy:
    def __init__(self, func: callable = None):
        self.func = func or (lambda *args, **kwargs: None)
        self.call_count = 0
        self.args = None

    @property
    def called(self):
        return self.call_count > 0

    def __call__(self, *args, **kwargs):
        self.call_count += 1
        self.args = args
        return self.func(*args, **kwargs)

    def reset(self):
        self.call_count = 0
        self.args = None

spy = Spy

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
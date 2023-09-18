from pynput.keyboard import Listener as KL
from pynput.mouse import Listener as ML


def watch_keyboard(on_release=None, on_press=None):
    # def on_release(key):
    with KL(on_release=on_release, on_press=on_press) as listener:
        listener.join()


def watch_mouse(on_click=None, on_move=None, on_scroll=None):
    # def on_click(x, y, button, pressed):
    with ML(on_click=on_click, on_move=on_move, on_scroll=on_scroll) as listener:
        listener.join()


def watch_all(keyboard=None, mouse=None):
    if not keyboard or not mouse:
        raise Exception("use watch_mouse or watch_keyboard")
    with KL(on_release=keyboard.get("on_release"), on_press=keyboard.get("on_press")) as kl, \
            ML(on_click=mouse.get("on_click"), on_move=mouse.get("on_move"), on_scroll=mouse.get("on_scroll")) as ml:
        kl.join()
        ml.join()

from arkitekt import App
from .manifest import identifier, version, logo
from arkitekt.builders import publicscheduleqt


global_app = None


def get_app_or_build_for_widget(widget) -> App:
    """ Get the app for the widget or build a new one if it does not exist"""
    print("Accessing Global App")
    global global_app
    if global_app is None:
        global_app = publicscheduleqt(identifier, version, parent=widget, logo=logo)
    return global_app


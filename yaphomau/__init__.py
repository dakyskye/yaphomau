import yaphomau.store as store
import yaphomau.ui as ui


def main():
    with store.connect():
        ui.event_loop()

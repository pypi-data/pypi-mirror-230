import sys
import time


def upgrade(device: str, image_name: str) -> None:
    # Pretend function that upgrades a device.
    # It's very convincing.
    print(f"Connecting to {device}...")
    time.sleep(2)
    print("Connected! Performing upgrade...")
    _pretend_loading_bar()
    print(f"{device} upgraded to {image_name}")


def _pretend_loading_bar() -> None:
    # As fake as Microsoft's
    bar = ""
    for i in range(9):
        sys.stdout.write(bar + "\r")
        sys.stdout.flush()
        bar += "."
        time.sleep(0.3)
    print("..........")

"""Read-only example, passive by default. Run through uv from the project root."""

RUN_HARDWARE = False
TARGET = "operator must select an exact configured name"


def main():
    if not RUN_HARDWARE:
        print("Hardware gate is off; no device access.")
        return
    from thorlabs_shutter_control import ShutterHub

    hub = ShutterHub("shutters.local.toml")
    try:
        print(hub.connect(TARGET))
        print(hub.get_status(TARGET))
    finally:
        hub.close()  # Passive release; this read-only example never changes output.


if __name__ == "__main__":
    main()

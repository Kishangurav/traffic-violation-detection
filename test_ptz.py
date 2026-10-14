from src.ptz.biomimetic_controller import BiomimeticOculomotorController

controller = BiomimeticOculomotorController(
    kp_pan=0.05,
    kp_tilt=0.05,
    dead_zone=20
)

frame_size = (1280, 720)

targets = [
    (640, 360),  # Target at center
    (650, 370),  # Target inside dead zone
    (800, 360),  # Target to the right
    (440, 360),  # Target to the left
    (640, 500),  # Target below center
]

for target in targets:
    pan_error, tilt_error = controller.calculate_error(
        target, frame_size
    )

    pan, tilt = controller.generate_commands(
        pan_error, tilt_error
    )

    print(f"\nTarget: {target}")
    print(f"Visual error: ({pan_error}, {tilt_error})")
    print(f"PTZ commands: pan={pan:.2f}, tilt={tilt:.2f}")

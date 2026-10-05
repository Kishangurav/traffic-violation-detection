class BiomimeticOculomotorController:
    """
    Simple biomimetic controller inspired by eye-movement control.

    It calculates the visual error between the target position
    and the camera center, then generates pan and tilt commands.
    """

    def __init__(self, kp_pan=0.05, kp_tilt=0.05, dead_zone=20):
        self.kp_pan = kp_pan
        self.kp_tilt = kp_tilt
        self.dead_zone = dead_zone

    def calculate_error(self, target_center, frame_size):
        target_x, target_y = target_center
        frame_width, frame_height = frame_size

        center_x = frame_width / 2
        center_y = frame_height / 2

        pan_error = target_x - center_x
        tilt_error = target_y - center_y

        return pan_error, tilt_error

    def generate_commands(self, pan_error, tilt_error):

        if abs(pan_error) <= self.dead_zone:
            pan_command = 0.0
        else:
            pan_command = self.kp_pan * pan_error

        if abs(tilt_error) <= self.dead_zone:
            tilt_command = 0.0
        else:
            tilt_command = self.kp_tilt * tilt_error

        return pan_command, tilt_command


__all__ = ["BiomimeticOculomotorController"]
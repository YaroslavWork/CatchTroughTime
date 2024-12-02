import pygame

from scripts.UI.text import Text


class Camera:

    def __init__(self, x: float, y: float, distance: float, resolution: tuple[int, int] = (640, 480)) -> None:
        self.x = x
        self.y = y
        self.distance = distance  # Distance for width (in meters)
        self.resolution = resolution

    def get_local_point(self, global_x: float, global_y: float) -> tuple:
        """
        This function convert global coordinates to local coordinates
        :param global_x: X coordinate in global coordinates
        :param global_y: Y coordinate in global coordinates
        :return: Local coordinates (x, y)
        """
        local_x = (global_x - self.x) * self.resolution[0] / self.distance
        local_y = (global_y - self.y) * self.resolution[0] / self.distance

        return local_x, local_y

    def get_global_point(self, local_x: float, local_y: float) -> tuple:
        """
        This function convert local coordinates to global coordinates
        :param local_x: X coordinate in local coordinates
        :param local_y: Y coordinate in local coordinates
        :return: Global coordinates (x, y)
        """
        global_x = local_x / self.resolution[0] * self.distance + self.x
        global_y = local_y / self.resolution[0] * self.distance + self.y

        return global_x, global_y

    def get_local_radius(self, r: float) -> float:
        """
        This function convert global radius to local radius
        :param r: Radius in global coordinates
        :return: Radius in local coordinates
        """
        return r * self.resolution[0] / self.distance

    def get_global_radius(self, r: float) -> float:
        """
        This function convert local radius to global radius
        :param r: Radius in local coordinates
        :return: Radius in global coordinates
        """
        return r / self.distance / self.resolution[0]

    def move_left(self, speed, dt) -> None:
        """
        This function move camera to the left side
        :param speed: The speed of a camera
        :param dt: Delta time
        :return: None
        """
        self.x -= speed * self.distance * dt / 1000

    def move_right(self, speed: float, dt: int) -> None:
        """
        This function move camera to the right side
        :param speed: The speed of a camera
        :param dt: Delta time
        :return: None
        """
        self.x += speed * self.distance * dt / 1000

    def move_up(self, speed: float, dt: int) -> None:
        """
        This function move camera to the up
        :param speed: The speed of a camera
        :param dt: Delta time
        :return: None
        """
        self.y -= speed * self.distance * dt / 1000

    def move_down(self, speed: float, dt: int) -> None:
        """
        This function move camera to the down
        :param speed: The speed of a camera
        :param dt: Delta time
        :return: None
        """
        self.y += speed * self.distance * dt / 1000

    def scale_in(self, speed_scale: float, dt: int) -> None:
        """
        This function change scale in the map
        :param speed_scale: The speed of a scale
        :param dt: Delta time
        :return: None
        """
        self.distance += self.distance * speed_scale * dt / 1000

    def scale_out(self, speed_scale: float, dt: int) -> None:
        """
        This function change scales out the map
        :param speed_scale: The speed of a scale
        :param dt: Delta time
        :return: None
        """
        self.distance -= self.distance * speed_scale * dt / 1000

    # This function draw map scale on the screen (the part of UI)
    def draw_map_scale(self, screen: pygame.Surface, min_pixels_scale: int = 50, max_pixels_scale: int = 200,
                       first_digital: tuple[int] = (1, 2, 5), offset: tuple[int, int] = (60, 10),
                       stick_width: int = 5) -> None:
        """
        This function draw map scale on the screen (the part of UI)
        :param screen: Screen for drawing
        :param min_pixels_scale: The value of min pixels scale
        :param max_pixels_scale: The value of max pixels scale
        :param first_digital: The first digital for scale (ex. (1, 2, 5))
        :param offset: Offset for scale (for UI)
        :param stick_width: Width of the stick
        :return: None
        """
        min_distance = min_pixels_scale / self.resolution[0] * self.distance  # Calculate distance for min pixels scale
        max_distance = max_pixels_scale / self.resolution[0] * self.distance  # Calculate distance for max pixels scale
        mean_distance = (min_distance + max_distance) / 2  # Mean distance

        # Find the closest digit to the mean distance (ex. if mean distance is 120, then the closest digit is 100)
        digit_amount = len(str(int(mean_distance)))  # Calculate amount of digits
        multiply = 10 ** (digit_amount - 1)  # Calculate multiply for the closest digit
        close_digit = mean_distance / multiply  # Calculate closest digit
        close_digit = min(first_digital, key=lambda x: abs(x - close_digit))  # Find the closest digit
        close_digit = close_digit * multiply  # Add multiplying to the closest digit

        # Calculate line length for the closest digit
        line_length = close_digit / self.distance * self.resolution[0]

        # Calculate line length (left and right points)
        left_pos = (self.resolution[0] - offset[0] - line_length, self.resolution[1] - offset[1])
        right_pos = (self.resolution[0] - offset[0], self.resolution[1] - offset[1])

        # Draw lines
        pygame.draw.line(screen, (0, 0, 0), left_pos, right_pos, 2)
        pygame.draw.line(screen,
                         (0, 0, 0),
                         (left_pos[0], left_pos[1] - stick_width),
                         (left_pos[0], left_pos[1] + stick_width),
                         2)
        pygame.draw.line(screen, (0, 0, 0),
                         (right_pos[0], right_pos[1] + stick_width),
                         (right_pos[0], right_pos[1] - stick_width),
                         2)

        # Text
        if close_digit >= 1000:
            Text(str(int(close_digit / 1000)) + " km", (0, 0, 0), 20) \
                .print(screen, (right_pos[0] + 30, right_pos[1]), True)
        else:
            Text(str(int(close_digit)) + " m", (0, 0, 0), 20) \
                .print(screen, (right_pos[0] + 30, right_pos[1]), True)

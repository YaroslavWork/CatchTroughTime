SIZE = [1080, 720]  # [width, height]
NAME = "Empty Pygame Project"  # Name of the window
FPS = 0  # 0 - unlimited
COLORS = {
    "background": (223, 223, 203)  # Background color
}


# Physics configuration
GRAVITY = (0, 0)  # Gravity vector
PLAYER_MASS = 5  # Mass of the player
PLAYER_RADIUS = 20  # Radius of the player
PLAYER_ELASTICITY = 0.8  # Elasticity of the player
PLAYER_FRICTION = 0.5  # Friction of the player
PLAYER_SPEED = 2000  # Speed of the player
WALL_ELASTICITY = 0.4  # Elasticity of the wall
DUMPING = 0.999  # Dumping of the player
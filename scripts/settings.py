SIZE = [1080, 720]  # [width, height]
NAME = "Empty Pygame Project"  # Name of the window
FPS = 0  # 0 - unlimited
DEBUG = False  # Debug mode
COLORS = {
    "background": (255, 249, 193),  # Background color
    "wall": (154, 151, 116), # Wall color
    "wall_contour": (0, 0, 0), # Wall contour color
    "catcher": (255, 56, 54), # Catcher color
    "runner": (50, 113, 252) # Runner color
}


# Physics configuration
GRAVITY = (0, 0)  # Gravity vector
PLAYER_MASS = 7  # Mass of the player
PLAYER_RADIUS = 20  # Radius of the player
PLAYER_ELASTICITY = 0.8  # Elasticity of the player
PLAYER_FRICTION = 0.5  # Friction of the player
PLAYER_SPEED = 2000  # Speed of the player
WALL_ELASTICITY = 0.8  # Elasticity of the wall
WALL_FRICTION = 0.5  # Friction of the wall
DUMPING = 0.999  # Dumping of the player
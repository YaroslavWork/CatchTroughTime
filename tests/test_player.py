import unittest

from scripts.player import Player, PlayerRole


class TestGetDistance(unittest.TestCase):

    def test_if_user_can_push_player_when_he_is_blocked(self):
        test_player = Player("test", "test", PlayerRole.CATCHER, [0, 0])
        
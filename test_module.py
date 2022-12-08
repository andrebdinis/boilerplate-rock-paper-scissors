import unittest
from RPS_game import play, mrugesh, abbey, quincy, kris
from RPS import player


class UnitTests(unittest.TestCase):
    print()

    def test_player_vs_quincy(self):
        print('-----------------------------------')
        print("Testing game against quincy...".upper())
        actual = play(player, quincy, 1000) >= 60
        self.assertTrue(
            actual,
            'Expected player to defeat quincy at least 60% of the time.')

    def test_player_vs_abbey(self):
        print('-----------------------------------')
        print("Testing game against abbey...".upper())
        actual = play(player, abbey, 1000) >= 60
        self.assertTrue(
            actual,
            'Expected player to defeat abbey at least 60% of the time.')

    def test_player_vs_kris(self):
        print('-----------------------------------')
        print("Testing game against kris...".upper())
        actual = play(player, kris, 1000) >= 60
        self.assertTrue(
            actual, 'Expected player to defeat kris at least 60% of the time.')

    def test_player_vs_mrugesh(self):
        print('-----------------------------------')
        print("Testing game against mrugesh...".upper())
        actual = play(player, mrugesh, 1000) >= 60
        self.assertTrue(
            actual,
            'Expected player to defeat mrugesh at least 60% of the time.')


if __name__ == "__main__":
    unittest.main()

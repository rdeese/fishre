import unittest
from count_tokens import *

class TestMatchers(unittest.TestCase):
    def test_lol_matcher(self):
        self.assertEqual(lol_matcher("lol"), ["lol"])
        self.assertEqual(lol_matcher("lolol"), ["lolol"])

        self.assertEqual(lol_matcher("LOL"), ["LOL"])
        self.assertEqual(lol_matcher("LolOLoL"), ["LolOLoL"])

        self.assertEqual(len(lol_matcher("ol")), 0)
        self.assertEqual(len(lol_matcher("lo")), 0)
        self.assertEqual(len(lol_matcher("lollipop")), 0)
        self.assertEqual(len(lol_matcher("olol")), 0)

        self.assertEqual(lol_matcher("lolllll"), ["lolllll"])
        self.assertEqual(lol_matcher("llllllol"), ["llllllol"])
        self.assertEqual(lol_matcher("looooool"), ["looooool"])

        self.assertEqual(len(lol_matcher("lolooolollollo")), 0)
        self.assertEqual(lol_matcher("lolooolollollol"), ["lolooolollollol"])

        self.assertEqual(lol_matcher("lol!"), ["lol!"])
        self.assertEqual(lol_matcher("lol!i cant even"), ["lol!"])
        self.assertEqual(lol_matcher("wow!lol."), ["!lol."])

        # problematic?
        self.assertEqual(len(lol_matcher("omglol")), 0)

    def test_repeated_character_matcher(self):
        self.assertEqual(len(repeated_character_matcher("haha")), 0)

        self.assertEqual(len(repeated_character_matcher("haa")), 0)

        matches = repeated_character_matcher("oook")
        self.assertEqual(matches, ["oook"])

        matches = repeated_character_matcher("haahahaaa ha")
        self.assertEqual(matches, ["haahahaaa"])

        matches = repeated_character_matcher("loooolllll")
        self.assertEqual(matches, ["loooolllll"])

        matches = repeated_character_matcher("!!!!!!!")
        self.assertEqual(matches, ["!!!!!!!"])
        
        self.assertEqual(len(repeated_character_matcher("...")), 0)
        self.assertEqual(len(repeated_character_matcher("a   b")), 0)

        matches = repeated_character_matcher(":DDDD")
        self.assertEqual(matches, [":DDDD"])

        matches = repeated_character_matcher("wOoOoO")
        self.assertEqual(matches, ["wOoOoO"])

        matches = repeated_character_matcher("ohhh yyyeaaah")
        self.assertEqual(matches, ["ohhh", "yyyeaaah"])

if __name__ == '__main__':
    unittest.main()

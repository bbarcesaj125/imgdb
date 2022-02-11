import unittest
from imgdb.utils import replace_every_nth


class TestUtils(unittest.TestCase):
    """Testing functions from utils file."""

    def setUp(self):
        self.formatted_string = replace_every_nth(
            50,
            " ",
            "\n",
            (
                "Prison Break: Created by Paul T. Scheuring. With Dominic "
                "Purcell, Wentworth Miller, Robert Knepper, Amaury "
                "Nolasco. Due to a political conspiracy, an innocent "
                "man is sent to death row and his only hope is his "
                "brother, who makes it his mission to deliberately "
                "get himself sent to the same prison in order to break "
                "the both of them out, from the inside."
            ),
        )

    def test_newline_every_nth(self):
        self.assertEqual(
            self.formatted_string,
            (
                "Prison Break: Created by Paul T. Scheuring. With Dominic "
                + "\n"
                + "             "
                "Purcell, Wentworth Miller, Robert Knepper, Amaury "
                + "\n"
                + "             "
                "Nolasco. Due to a political conspiracy, an innocent "
                + "\n"
                + "             "
                "man is sent to death row and his only hope is his "
                + "\n"
                + "             "
                "brother, who makes it his mission to deliberately "
                + "\n"
                + "             "
                "get himself sent to the same prison in order to break "
                + "\n"
                + "             "
                "the both of them out, from the inside."
            ),
            "Malformatted text!",
        )

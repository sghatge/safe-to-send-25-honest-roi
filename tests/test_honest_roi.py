import unittest

from honest_roi import analyse, load


def arm(mins):
    return [{"minutes": m, "found": 1, "planted": 1} for m in mins]


class RoiTest(unittest.TestCase):
    def test_refuses_small_samples(self):
        with self.assertRaises(ValueError):
            analyse({"manual": arm([10, 12, 11]), "tool": arm([5, 6, 4, 5, 6])})

    def test_illustrative_file_loads_and_skips_comment(self):
        arms = load("examples/illustrative_trials.csv")
        self.assertEqual(len(arms["manual"]), 6)
        r = analyse(arms)
        self.assertGreater(r["saving"], 0)
        self.assertLessEqual(r["interval"][0], r["saving"])
        self.assertLessEqual(r["saving"], r["interval"][1])

    def test_recall_reported(self):
        r = analyse({"manual": arm([10] * 5), "tool": arm([5] * 5)})
        self.assertEqual(r["recall"], (1.0, 1.0))


if __name__ == "__main__":
    unittest.main()

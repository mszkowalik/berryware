import unittest
import os
from adapters.persist import Persist

class TestPersist(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.filename = "_persist_test.json"
        Persist._instance = None  # Resetting the singleton instance for testing
        cls.persist = Persist(cls.filename)

    @classmethod
    def tearDownClass(cls):
        # Remove the test file after all tests
        if os.path.exists(cls.filename):
            os.remove(cls.filename)

    def setUp(self):
        self.persist.zero()
        self.persist.save()

    def test_set_and_get_attribute(self):
        self.persist.a = 1
        self.assertEqual(self.persist.a, 1)

    def test_save_and_load(self):
        self.persist.a = 1
        self.persist.save()

        new_persist = Persist(self.filename)
        self.assertEqual(new_persist.a, 1)

    def test_has_key(self):
        self.persist.a = 1
        self.assertTrue(self.persist.has("a"))
        self.assertFalse(self.persist.has("b"))

    def test_remove_key(self):
        self.persist.a = 1
        self.assertTrue(self.persist.remove("a"))
        self.assertFalse(self.persist.has("a"))
        self.assertFalse(self.persist.remove("b"))

    def test_find_key(self):
        self.persist.a = 1
        self.assertEqual(self.persist.find("a"), 1)
        self.assertIsNone(self.persist.find("b"))
        self.assertEqual(self.persist.find("b", "default"), "default")

    def test_member_key(self):
        self.persist.a = 1
        self.assertEqual(self.persist.member("a"), 1)
        self.assertIsNone(self.persist.member("b"))

    def test_setmember(self):
        self.persist.setmember("a", 1)
        self.assertEqual(self.persist.a, 1)

    def test_zero(self):
        self.persist.a = 1
        self.persist.b = 2
        self.persist.zero()
        self.assertIsNone(self.persist.a)
        self.assertIsNone(self.persist.b)

    def test_singleton(self):
        another_persist = Persist(self.filename)
        another_persist.a = 10
        self.assertEqual(self.persist.a, 10)

if __name__ == '__main__':
    unittest.main()

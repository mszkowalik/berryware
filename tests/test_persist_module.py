import unittest
import os
from adapters.persist_adapter import PersistAdapter

class TestPersist(unittest.TestCase):
    
    def setUp(self):
        self.filename = "_persist_test.json"
        self.persist = PersistAdapter(self.filename)
        self.persist.zero()
        self.persist.save()

    def tearDown(self):
        # Remove the test file after each test
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_set_and_get_attribute(self):
        self.persist.a = 1
        self.assertEqual(self.persist.a, 1)

    def test_save_and_load(self):
        self.persist.a = 1
        self.persist.save()

        new_persist = PersistAdapter(self.filename)
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

if __name__ == '__main__':
    unittest.main()

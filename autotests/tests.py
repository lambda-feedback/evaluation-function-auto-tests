import unittest

from .autotests import TestFile

class TestFileLoad(unittest.TestCase):
    
    def test_basic(self):
        test_file = {}
        try:
            test_file = TestFile("""
---
title: Test
tests:
    - description: Test
      answer: "foo"
      response: "bar"
      expected_result:
        is_correct: yes
""", "test.yaml")
        except:
            self.fail()
        
        test1 = test_file.groups[0]["tests"][0]
        self.assertEqual(test1.answer, "foo")
        self.assertEqual(test1.sub_tests[0].response, "bar")
        self.assertEqual(test1.sub_tests[0].is_correct, True)
    
    def test_missing_content(self):
        try:
            TestFile("""
---
title: Test
tests:
    - description: Test
      answer: "foo"
      response: "bar"
""", "test.yaml")
            self.fail()
        except:
            pass
    
    def test_sub_tests(self):
        test_file = {}
        try:
            test_file = TestFile("""
---
title: Test
tests:
    - description: Test
      answer: "foo"
      sub_tests:
        - response: "bar"
          expected_result:
            is_correct: yes
        - response: "baz"
          expected_result:
            is_correct: yes
""", "test.yaml")
        except:
            self.fail()
        
        test1 = test_file.groups[0]["tests"][0]
        self.assertEqual(len(test1.sub_tests), 2)
        self.assertEqual(test1.sub_tests[0].response, "bar")
        self.assertEqual(test1.sub_tests[1].response, "baz")

    def test_groups(self):
        test_file = {}
        try:
            test_file = TestFile("""
---
title: Test Group 1
tests:
    - description: Test1
      answer: "foo"
      response: "bar"
      expected_result:
        is_correct: yes
---
title: Test Group 2
tests:
    - description: Test2
      answer: "foo"
      response: "bar"
      expected_result:
        is_correct: no
""", "test.yaml")
        except:
            self.fail()
        
        self.assertEqual(test_file.groups[1]["title"], "Test Group 2")
        test1 = test_file.groups[1]["tests"][0]
        self.assertEqual(test1.answer, "foo")
        self.assertEqual(test1.sub_tests[0].response, "bar")
        self.assertEqual(test1.sub_tests[0].is_correct, False)

    def test_exclude(self):
        test_file = {}
        try:
            test_file = TestFile("""
---
title: Test Group 1
tests:
    - description: Test1
      answer: "foo"
      exclude_from_docs: yes
      sub_tests: 
        - response: "bar"
          expected_result:
            is_correct: yes
        - response: "baz"
          expected_result:
            is_correct: yes
""", "test.yaml")
        except:
            self.fail()
        test = test_file.groups[0]["tests"][0]
        self.assertTrue(test.sub_tests[0].exclude_from_docs)
        self.assertTrue(test.sub_tests[1].exclude_from_docs)

"""
Basic tests that don't require external dependencies
"""
import unittest
from unittest.mock import Mock


class TestBasicFunctionality(unittest.TestCase):
    """基本的な機能のテスト（外部依存なし）"""
    
    def test_mock_functionality(self):
        """Mock機能のテスト"""
        mock_obj = Mock()
        mock_obj.test_method.return_value = "test_result"
        
        result = mock_obj.test_method()
        self.assertEqual(result, "test_result")
        mock_obj.test_method.assert_called_once()
    
    def test_basic_calculations(self):
        """基本的な計算のテスト"""
        self.assertEqual(2 + 2, 4)
        self.assertEqual(10 - 5, 5)
        self.assertEqual(3 * 4, 12)
        self.assertEqual(8 / 2, 4)
    
    def test_string_operations(self):
        """文字列操作のテスト"""
        test_str = "Hello, World!"
        self.assertEqual(test_str.upper(), "HELLO, WORLD!")
        self.assertEqual(test_str.lower(), "hello, world!")
        self.assertTrue(test_str.startswith("Hello"))
        self.assertTrue(test_str.endswith("World!"))
    
    def test_list_operations(self):
        """リスト操作のテスト"""
        test_list = [1, 2, 3, 4, 5]
        self.assertEqual(len(test_list), 5)
        self.assertEqual(test_list[0], 1)
        self.assertEqual(test_list[-1], 5)
        
        test_list.append(6)
        self.assertEqual(len(test_list), 6)
        self.assertEqual(test_list[-1], 6)
    
    def test_dict_operations(self):
        """辞書操作のテスト"""
        test_dict = {"key1": "value1", "key2": "value2"}
        self.assertEqual(test_dict["key1"], "value1")
        self.assertEqual(len(test_dict), 2)
        
        test_dict["key3"] = "value3"
        self.assertEqual(len(test_dict), 3)
        self.assertIn("key3", test_dict)


if __name__ == '__main__':
    unittest.main()
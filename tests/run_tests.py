#!/usr/bin/env python3
"""
テスト実行スクリプト

使用方法:
    python tests/run_tests.py          # 全てのテストを実行
    python tests/run_tests.py generator # generatorテストのみ実行
    python tests/run_tests.py evaluator # evaluatorテストのみ実行
"""

import sys
import unittest
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_generator_tests():
    """generatorテストを実行"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName('tests.test_generator')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


def run_evaluator_tests():
    """evaluatorテストを実行"""
    loader = unittest.TestLoader()
    
    # 各テストファイルをロード
    test_modules = [
        'tests.test_evaluator',
        'tests.test_evaluator_libs',
        'tests.test_agents_evaluator'
    ]
    
    suite = unittest.TestSuite()
    for module in test_modules:
        suite.addTests(loader.loadTestsFromName(module))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


def run_all_tests():
    """全てのテストを実行"""
    print("=== Generator Tests ===")
    generator_success = run_generator_tests()
    
    print("\n=== Evaluator Tests ===")
    evaluator_success = run_evaluator_tests()
    
    print("\n=== Test Summary ===")
    print(f"Generator Tests: {'PASSED' if generator_success else 'FAILED'}")
    print(f"Evaluator Tests: {'PASSED' if evaluator_success else 'FAILED'}")
    
    return generator_success and evaluator_success


def main():
    """メイン関数"""
    if len(sys.argv) > 1:
        target = sys.argv[1].lower()
        
        if target == 'generator':
            success = run_generator_tests()
        elif target == 'evaluator':
            success = run_evaluator_tests()
        else:
            print(f"Unknown target: {target}")
            print("Available targets: generator, evaluator")
            return False
    else:
        success = run_all_tests()
    
    return success


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
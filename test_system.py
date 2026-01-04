#!/usr/bin/env python3
"""
Test script for weather alert bot components.
Run this to verify all components are working correctly.
"""

import sys
import os
from pathlib import Path


def test_imports():
    """Test that all required modules can be imported."""
    print("testing imports...")
    
    try:
        import yaml
        print("  ✅ pyyaml")
    except ImportError:
        print("  ❌ pyyaml not installed")
        return False
    
    try:
        import requests
        print("  ✅ requests")
    except ImportError:
        print("  ❌ requests not installed")
        return False
    
    try:
        import telegram
        print("  ✅ python-telegram-bot")
    except ImportError:
        print("  ❌ python-telegram-bot not installed")
        return False
    
    try:
        import schedule
        print("  ✅ schedule")
    except ImportError:
        print("  ❌ schedule not installed")
        return False
    
    try:
        from dotenv import load_dotenv
        print("  ✅ python-dotenv")
    except ImportError:
        print("  ❌ python-dotenv not installed")
        return False
    
    return True


def test_project_modules():
    """Test that all project modules can be imported."""
    print("\ntesting project modules...")
    
    modules = [
        'config_loader',
        'weather_monitor',
        'alert_manager',
        'telegram_bot',
        'logger_utils'
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except Exception as e:
            print(f"  ❌ {module}: {e}")
            all_ok = False
    
    return all_ok


def test_configuration():
    """Test configuration loading."""
    print("\ntesting configuration...")
    
    try:
        from config_loader import ConfigLoader
        
        # check if config file exists
        if not Path('config.yaml').exists():
            print("  ⚠️  config.yaml not found (this is ok for new setup)")
            return True
        
        # check if .env exists
        if not Path('.env').exists():
            print("  ⚠️  .env not found - copy env.example to .env and configure")
            return True
        
        # try loading config
        try:
            config_loader = ConfigLoader()
            config = config_loader.load()
            print("  ✅ configuration loaded successfully")
            
            # validate key sections
            if 'locations' in config:
                print(f"  ✅ found {len(config['locations'])} location(s)")
            
            if 'alerts' in config:
                enabled_alerts = sum(
                    1 for k, v in config['alerts'].items()
                    if isinstance(v, dict) and v.get('enabled', False)
                )
                print(f"  ✅ found {enabled_alerts} enabled alert type(s)")
            
            return True
            
        except Exception as e:
            print(f"  ❌ error loading configuration: {e}")
            return False
            
    except Exception as e:
        print(f"  ❌ error: {e}")
        return False


def test_file_structure():
    """Test that all required files exist."""
    print("\ntesting file structure...")
    
    required_files = [
        'config.yaml',
        'requirements.txt',
        'README.md',
        'setup_telegram_bot.md',
        'main.py',
        'config_loader.py',
        'weather_monitor.py',
        'alert_manager.py',
        'telegram_bot.py',
        'logger_utils.py'
    ]
    
    optional_files = [
        '.env',
        'env.example'
    ]
    
    all_ok = True
    
    for file in required_files:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} missing")
            all_ok = False
    
    for file in optional_files:
        if Path(file).exists():
            print(f"  ✅ {file} (optional)")
        else:
            print(f"  ⚠️  {file} not found (optional)")
    
    return all_ok


def main():
    """Run all tests."""
    print("=" * 60)
    print("weather alert bot - system test")
    print("=" * 60)
    print()
    
    results = []
    
    # run tests
    results.append(("dependencies", test_imports()))
    results.append(("modules", test_project_modules()))
    results.append(("file structure", test_file_structure()))
    results.append(("configuration", test_configuration()))
    
    # summary
    print("\n" + "=" * 60)
    print("test summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ passed" if passed else "❌ failed"
        print(f"{test_name:20s}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✨ all tests passed!")
        print("\nnext steps:")
        print("  1. configure .env with your api keys")
        print("  2. edit config.yaml with your locations")
        print("  3. run: python main.py --check-now")
    else:
        print("⚠️  some tests failed")
        print("\nif dependencies failed:")
        print("  run: pip install -r requirements.txt")
        print("\nif configuration failed:")
        print("  1. copy env.example to .env")
        print("  2. add your api keys to .env")
        print("  3. edit config.yaml")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())


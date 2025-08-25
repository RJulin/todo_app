#!/usr/bin/env python3
"""
Simple test runner for the Todo App backend
"""

import subprocess
import sys
import os

def run_tests():
    """Run all tests"""
    print("🚀 Running tests...")
    
    # Get the backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    # Check if we're in a virtual environment
    venv_python = os.path.join(backend_dir, '.venv', 'bin', 'python')
    
    if os.path.exists(venv_python):
        python_cmd = venv_python
        print(f"Using virtual environment Python: {python_cmd}")
    else:
        python_cmd = sys.executable
        print(f"Using system Python: {python_cmd}")
    
    try:
        result = subprocess.run([
            python_cmd, "-m", "pytest", 
            "-v"
        ], check=True)
        
        print("All tests passed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Tests failed with exit code: {e.returncode}")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 
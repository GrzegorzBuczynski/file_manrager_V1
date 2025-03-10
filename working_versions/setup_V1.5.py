import subprocess
import sys
import os
import shutil

def create_venv():
    """Create and activate a virtual environment."""
    print("Creating a virtual environment...")
    
    # Check if python3-venv is installed
    try:
        # First, try installing python3-venv
        subprocess.check_call(["sudo", "apt", "install", "-y", "python3-full", "python3-venv"])
    except subprocess.CalledProcessError:
        print("Failed to install python3-venv. Please install it manually.")
        sys.exit(1)
    
    # Create virtual environment
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv")
    
    # Remove existing venv if it exists
    if os.path.exists(venv_path):
        print(f"Removing existing virtual environment at {venv_path}")
        shutil.rmtree(venv_path)
    
    try:
        subprocess.check_call([sys.executable, "-m", "venv", venv_path])
        print(f"Virtual environment created at {venv_path}")
        
        # Return paths to python and pip in the virtual environment
        python_path = os.path.join(venv_path, "bin", "python")
        pip_path = os.path.join(venv_path, "bin", "pip")
        
        return python_path, pip_path
    except subprocess.CalledProcessError:
        print("Failed to create virtual environment.")
        sys.exit(1)

def install_system_dependencies():
    """Install system dependencies using apt."""
    try:
        print("Updating package lists...")
        subprocess.check_call(["sudo", "apt", "update"])
        
        print("Installing system dependencies...")
        # Install system dependencies that might be required for OpenCV and Pillow
        dependencies = [
            "python3-full",
            "build-essential",
            "cmake",
            "pkg-config",
            "libopencv-dev",
            "libjpeg-dev",
            "libpng-dev",
            "libtiff-dev",
            "tk-dev",
            "python3-tk"  # Required for Tkinter GUI applications
        ]
        
        subprocess.check_call(["sudo", "apt", "install", "-y"] + dependencies)
        print("System dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install system dependencies: {e}")
        sys.exit(1)

def install_python_dependencies(pip_path):
    """Install required Python packages in the virtual environment."""
    required_packages = [
        "opencv-python",
        "pillow",  # PIL/Pillow for image processing
        "numpy",   # Often required by OpenCV
        "matplotlib",  # For any visualization needs
        "tqdm"     # For progress bars if needed
    ]
    
    # Install each package and handle potential errors
    for package in required_packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([pip_path, "install", package])
            print(f"{package} installed successfully.")
        except subprocess.CalledProcessError:
            print(f"Failed to install {package}. Please install it manually.")
            
def create_activation_script():
    """Create a simple shell script to activate and run the application."""
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_app.sh")
    
    with open(script_path, "w") as f:
        f.write("#!/bin/bash\n")
        f.write(f"source {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'venv/bin/activate')}\n")
        f.write("python file_manager.py\n")
    
    # Make the script executable
    os.chmod(script_path, 0o755)
    print(f"Created executable script at {script_path}")
    print("You can now run your application with: ./run_app.sh")

def main():
    # Install necessary system packages
    install_system_dependencies()
    
    # Create a virtual environment
    python_path, pip_path = create_venv()
    
    # Upgrade pip in the virtual environment
    print("Upgrading pip in virtual environment...")
    try:
        subprocess.check_call([python_path, "-m", "pip", "install", "--upgrade", "pip"])
    except subprocess.CalledProcessError:
        print("Failed to upgrade pip in virtual environment.")
        sys.exit(1)
    
    # Install all required Python packages
    install_python_dependencies(pip_path)
    
    # Test if OpenCV can be imported
    print("\nTesting installations...")
    modules_to_test = ["cv2", "PIL", "numpy"]
    for module in modules_to_test:
        try:
            if module == "PIL":
                cmd = "from PIL import Image; print('PIL/Pillow version:', Image.__version__)"
            else:
                cmd = f"import {module}; print('{module} version:', {module}.__version__)"
                
            result = subprocess.run([python_path, "-c", cmd], 
                                   capture_output=True, text=True)
            if result.returncode == 0:
                print(result.stdout.strip())
            else:
                print(f"Failed to import {module}. Error: {result.stderr}")
        except Exception as e:
            print(f"Error testing {module}: {e}")
    
    # Create an activation and run script
    create_activation_script()
    
    print("\nSetup completed successfully!")
    print(f"To activate the virtual environment, run: source {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'venv/bin/activate')}")
    print("After activation, you can run your Python scripts with the installed packages.")
    print("Alternatively, use the created run_app.sh script to run your application.")

if __name__ == "__main__":
    main()
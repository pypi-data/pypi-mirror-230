import os

# bundles brick files are inserted in same directory during build process

def package_dir():
    return os.path.dirname(os.path.abspath(__file__))

def bundle_path():
    return f"{package_dir()}/../oos/install/brick"

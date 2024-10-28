try:
    import pkg_resources
except:
    # subprocess.run(['pip', 'install', 'setuptools'], check=True)
    # import pkg_resources
    print(f"\n\tERROR: pkg_resources missing. (this is a built-in system library)")
    print(f'\tUpdate base libraries by running: `pip install setuptools`')
    exit(1)
from typing import List
import subprocess
import os
import shutil
import sys
from Terminal import running_on_PowerShell, is_running_on_mac, is_externally_managed

def check_venv_module():
    """Check if the venv module is available."""
    try:
        import venv
        return True
    except ImportError:
        return False

def is_running_in_virtualenv():
    """Check if the script is running inside a virtual environment."""
    return (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))

def sample_run():
    unpack(
        [ 'argon2-cffi', 'cryptography', 'colorama', 'readline', 'yubico-client', 'pyotp', 'qrcode', 'pillow', 'qrcode-terminal', 'qrcode' ],
        [ 'argon2-cffi', 'cryptography', 'colorama', 'pyreadline', 'yubico-client', 'pyotp', 'qrcode', 'pillow', 'qrcode-terminal', 'qrcode' ]
    )

def unpack(
    bash_packages: List[str], 
    powershell_packages: List[str],
    _base_install_command: List[str] = ['python3', '-m', 'pip', 'install'],
    _mac_install_command: List[str] = ['python3', '-m', 'venv', 'install']
    ):
    print(f'  <<< PACKAGE MANAGER :: VERIFYING ALL REQUIRED PACKAGES >>>', end='\r')
    installed_packages = [package.key for package in pkg_resources.working_set]
    required_packages = bash_packages if not running_on_PowerShell() else powershell_packages

    install_command = _base_install_command
        
    # Detect macOS environment
    if is_running_on_mac():  
        install_command = _mac_install_command  # Modify command for macOS if needed
    
    # Check if the environment is externally managed
    if is_externally_managed() and not is_running_in_virtualenv():
        # Recommend virtual environment creation
        print(f"\n\tERROR: This is an externally managed environment.")
        print(f"\tWARNING: Creating and using a virtual environment is recommended.")
        
        # Check if 'venv' module is available
        if not check_venv_module():
            print(f"\tERROR: The python3-venv package is missing. Install it with: `sudo apt install python3-venv`")
            # print("\tsudo apt install python3-venv")
            sys.exit(1)  # Exit the script if venv is not installed
        
        venv_dir = os.path.join(os.getcwd(), 'venv')
        if not os.path.exists(venv_dir):
            print(f"\tCreating virtual environment...")
            try:
                subprocess.run(['python3', '-m', 'venv', venv_dir], check=True)
            except subprocess.CalledProcessError as e:
                print(f"ERROR: Failed to create virtual environment: {e}")
                print("Please install the `python3-venv` package and try again.")
                sys.exit(1)
        
        print(f"\tActivating virtual environment...")
        # activate_venv = os.path.join(venv_dir, 'bin', 'activate')
        # os.system(f"source {activate_venv}")
        result = subprocess.run(['python3', '-m', 'venv', '.venv'], check=True)
        if result != 0:
            print(f"\tERROR: Response from `python3 -m venv .venv` was non zero value 1.")
            print(f"\tERROR: You must be in a virtual environment to continue...")
            # if input(f"\tContinue anyway? (Y/n) > ").lower() not in ['y', 'yes']:
            print(f"\tPlease run the following commands and try again:")
            print(f"\t\tpython3 -m venv .venv")
            print(f"\t\tsource .venv/bin/activate")
            exit(1)
        result = subprocess.run(['source', '.venv/bin/activate'], check=True)
        if result == 0:
            print(f"\tStarted virtual environment successfully! To leave the virtual environment run `deactivate`")
        else:
            print(f"\tERROR: Could not enter the virtual environment? - maybe try `source .venv/bin/activate`?")
            exit(1)
        # install_command = [os.path.join(venv_dir, 'bin', 'python'), '-m', 'pip', 'install']
    elif is_running_in_virtualenv():
        print(f'\n\tVirtual environment detected...')
        print(f'\t(you may leave the virtual environment anytime by running `deactivate`)')
    
    for required_package in required_packages:
        if required_package not in installed_packages:
            print(f'\n\t{required_package} not installed. Installing...')
            try:
                result = subprocess.run(install_command + [required_package], check=True)
                # result = subprocess.run(
                #     ['python3', '-m', 'pip', 'install', required_package], #['pip', 'install', required_package] if required_package != 'colorama' else ['python3', '-m', 'pip', 'install', 'colorama'], 
                #     check=True)
                if result.returncode == 0:
                    print(f'\t{required_package} installed successfully.\n')
                else:
                    print(f'\tERROR: Failed to install "{required_package}" - maybe try pip install {required_package}?')
            except pkg_resources.DistributionNotFound:
                raise Exception(f'\tERROR: Unable to install "{required_package}"')
            except subprocess.CalledProcessError as e:
                if required_package != 'readline':
                    raise e
                if input("FOR DEBUG ONLY: See full error? (Y/n) > ").lower() in ['y', 'yes']:
                    raise e
                print(f'\n\tCaught error (dependency missing) for package "readline".')
                print('\tPlease run the following and try again:')
                print('\t\tsudo apt install libncurses5-dev libncursesw5-dev')
                print('\t\tsudo apt install libncurses-dev')
    print(' ' * len(' <<< PACKAGE MANAGER :: VERIFYING ALL REQUIRED PACKAGES >>>'))

import sys
import os

# Ensure the current directory is in the sys.path for module imports
current_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_directory)

# Import mock modules
import mqtt_adapter as mqtt
import tasmota_adapter as tasmota

# Import autoexec module
import autoexec

# Run the main function from autoexec
if __name__ == "__main__":
    try:
        autoexec.main()
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

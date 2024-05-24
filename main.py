import sys
from berry_converter import convert_python_to_berry

def main():
    input_file = 'autoexec.py'

    if not os.path.exists(input_file):
        print(f"Error: {input_file} does not exist.")
        return

    convert_python_to_berry(input_file)

if __name__ == '__main__':
    main()

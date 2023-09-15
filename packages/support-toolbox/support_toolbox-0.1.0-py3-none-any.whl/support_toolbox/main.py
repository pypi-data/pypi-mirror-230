import os
import importlib


def main():
    print("Welcome to Support Toolbox!")

    # Get the absolute path to the 'support_toolbox' package directory
    package_dir = os.path.dirname(os.path.abspath(__file__))

    # List available tools
    tools = [f[:-3] for f in os.listdir(package_dir) if f.endswith('.py') and f != '__init__.py' and f != 'main.py']

    # Display the available tools
    print("Available tools:")
    for idx, tool in enumerate(tools, start=1):
        print(f"{idx}. {tool}")

    # Ask the user to select a tool
    selection = input("Enter the number of the tool you want to use: ")

    try:
        selected_tool = tools[int(selection) - 1]
        module = importlib.import_module(f"support_toolbox.{selected_tool}")
        module.run()
    except (ValueError, IndexError):
        print("Invalid selection. Please enter a valid number.")


if __name__ == "__main__":
    main()

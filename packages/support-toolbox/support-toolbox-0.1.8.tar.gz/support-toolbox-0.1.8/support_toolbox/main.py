import os
import importlib
from support_toolbox import utils


def main():
    print("\nWelcome to the Support Toolbox!\n")

    # Get the absolute path to the 'support_toolbox' package directory
    package_dir = os.path.dirname(os.path.abspath(__file__))

    # List available tools
    tools = [f[:-3] for f in os.listdir(package_dir) if f.endswith('.py') and f != '__init__.py' and f != 'main.py' and f != 'utils.py']

    # Display the available tools
    print("Available tools:")
    for idx, tool in enumerate(tools, start=1):
        print(f"{idx}. {tool}")

    # Ask the user to select a tool
    selection = input("\nEnter the number corresponding with the tool you want to use: ")

    try:
        selected_tool = tools[int(selection) - 1]

        # Check if the tokens for the selected tool exist and set them up if needed
        utils.check_tokens(selected_tool)

        module = importlib.import_module(f"support_toolbox.{selected_tool}")
        module.run()
    except (ValueError, IndexError):
        print("Invalid selection. Please enter a valid number.")


if __name__ == "__main__":
    main()

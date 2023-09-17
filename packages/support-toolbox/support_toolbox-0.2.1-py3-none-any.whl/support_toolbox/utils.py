import os
import configparser

# List of tools and their corresponding token names
tools = {
    "delete_users": ["DWSUPPORT_API_TOKEN", "JIRA_API_TOKEN", "JIRA_USERNAME"]
    # Add more tools and token names as needed here
}


def check_tokens(selected_tool):
    user_home = os.path.expanduser("~")
    config_file_path = os.path.join(user_home, ".tokens.ini")

    config = configparser.ConfigParser()

    if os.path.exists(config_file_path):
        config.read(config_file_path)

    if selected_tool not in config:
        config[selected_tool] = {}

    for token_name in tools.get(selected_tool, []):
        if token_name not in config[selected_tool]:
            token_value = input(f"Enter {token_name} for {selected_tool}: ")
            config[selected_tool][token_name] = token_value

    with open(config_file_path, "w") as configfile:
        config.write(configfile)

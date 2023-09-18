# support-toolbox
A suite of CLI tools for the support team contained within a Python package 

## Current Release
[Version 0.2.2](https://pypi.org/manage/project/support-toolbox/releases/)


## Purpose

The `support-toolbox` package is a collection of CLI tools designed to simplify and automate tasks by abstracting from direct interaction with APIs and manual processes. Currently, the toolbox supports automating:
```
Available tools:
1. create_service_accounts
2. delete_users
3. clear_user_layer
4. deploy_integrations
5. deploy_browse_card
```
- more to come (revert soft deletes)

**To Show Current Version:**
```bash
pip show support-toolbox
```

**To Upgrade:**
```bash
pip install --upgrade support-toolbox
```


### Dependencies
1. Clone [cli](https://github.com/datadotworld/cli) and [integration-templates](https://github.com/datadotworld/integration-templates) to the following directories:
   
```bash
git clone YOUR_CLI_SSH_URL ~/.dw/cli
   ```

```bash
git clone YOUR_INTEGRATION_TEMPLATES_SSH_URL ~/
   ```

2. Configure your systems path to include the `cli` file
```bash
   export PATH=${PATH}:${HOME}/.dw/cli/bin
```


## How to Use

**Install Python:**

1. Make sure Python is installed on your computer. If it's not, you can download and install it from the official Python website: [Python Downloads](https://www.python.org/downloads/).
2. During installation, ensure you check the option to add Python to your system's PATH.

**Install Package:**

3. Open a terminal or command prompt.
4. Install the package from PyPI using `pip`:

   ```bash
   pip install support-toolbox
   ```
**Run the CLI Tool:**

5. After successful installation, you can run the CLI tool from your terminal by using the package name:

   ```bash
   support-toolbox
   ```

## Using a Tool for the First Time
When using these tools for the first time, you will encounter two types of tokens: permanent and runtime.

### Permanent Tokens

During the initial setup, you'll be prompted to provide these tokens for specific tools. If you make a mistake during this setup, don't worry; you can reset your tokens.

To reset your tokens:

1. Open a terminal.
2. Use the `cd` command to navigate to your Home directory:

  ```bash
   cd ~
   ```
3. Run the following command to reset your tokens:


  ```bash
  rm -rf .tokens.ini
  ```
This command will remove the token file, allowing you to reconfigure your tokens when you launch the tool again.

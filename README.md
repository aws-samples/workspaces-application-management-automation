[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)  ![GitHub](https://img.shields.io/github/license/aws-samples/workspaces-application-management-automation) [![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

# Automate removal of license included Microsoft Office for Amazon WorkSpaces

Customers have asked how they can migrate their users from the license included version of Office to M365 licenses they already own.  Previously, administrators could only remove application bundles through the WorkSpaces migration process, which creates a new root volume while keeping the user volume intact. The migration option is still available, but now customers can also use the new [manage applications](https://docs.aws.amazon.com/workspaces/latest/adminguide/manage-applications.html) feature to do the same. This blog guides you on how to remove Office from existing WorkSpaces bundle running on WorkSpaces using the new APIs that the manage applications feature provides. In the examples below, you learn how to identify and remove Office license included from your WorkSpaces using either standalone PowerShell scripts or an AWS Lambda function.

This repository contains the supporting scripts for the AWS Desktop and Application Streaming blog article [Automate removal of license included Microsoft Office for Amazon WorkSpaces](https://aws.amazon.com/blogs/desktop-and-application-streaming/preparing-to-migrate-to-microsoft-365-apps-at-scale-on-amazon-workspaces/). Please refer to the blog article for additional guidance on deploying the scripts provided in this repository. 

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.


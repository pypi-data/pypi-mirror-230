# Streamline AWS CloudFormation Custom Resource Management with Python's `cfnresponse2`

Simplify the management of custom resources in AWS CloudFormation, especially within AWS Lambda environments, using the `cfnresponse2` Python package.

## Installation

You can effortlessly install the `cfnresponse2` package via pip:

```bash
pip install cfnresponse2
```

Alternatively, you have the option to download it directly or upload it to Amazon S3:

```python
import urllib3
import sys
import os

# Download cfnresponse2.py from GitHub or upload it to Amazon S3
github_raw_url = "https://raw.githubusercontent.com/ggiallo28/cfnresponse/master/cfnresponse/__init__.py"

with open("cfnresponse2.py", 'wb') as out_file, urllib3.PoolManager() as http:
    out_file.write(http.request('GET', github_raw_url).data)

# Add the package to your Python path
sys.path.append("cfnresponse2.py")

# Import the cfnresponse2 module
from cfnresponse2 import register_handler, lambda_handler
```

## Practical Use Cases

`cfnresponse2` is designed with AWS Lambda functions in mind, serving as custom resource handlers in CloudFormation stacks. It simplifies CloudFormation operations such as creating, updating, and deleting custom resources. This empowers you to execute custom logic during stack operations.

For comprehensive examples showcasing effective usage of the `cfnresponse2` package, explore the [samples](https://github.com/ggiallo28/cfnresponse/tree/907255318ae6bea3729818036c20c323f5790952/samples) directory within the repository. These samples cover various scenarios of custom resource management within CloudFormation.

## Repository Structure

The project repository is organized as follows:

- `cfnresponse`: Houses the `__init__.py` file, serving as the core of the `cfnresponse2` module.
- `LICENSE`: Contains licensing information associated with the package.
- `README.md`: The document you are currently reading, offering essential instructions for usage.
- `samples`: Contains sample Lambda functions that provide practical demonstrations of `cfnresponse2` usage. The actual code resides in the repository, not within this README.
- `setup.py`: A configuration file for setting up the package.
- `tests`: Contains test cases tailored to evaluate the functionality of the `cfnresponse2` package.

## Important Note

`cfnresponse2` maintains compatibility with Amazon Web Services (AWS) `cfnresponse` module, readily available within Python AWS Lambda environments. You can seamlessly update your code with this package, ensuring a smooth transition without disruptions.
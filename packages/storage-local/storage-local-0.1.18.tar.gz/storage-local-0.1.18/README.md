# storage-local-python-package

# pypi package
https://pypi.org/project/storage-local/<br>

# Simplified example of usage
tests/test_circles_storage.py<br>

# Create requirments.txt
pip install pipreqs<br>
pipreqs .<br>

# Install all dependencies
cd <root-directory-where-requirments.txt>
pip install -r requirements.txt<br>

# If we want to install requirments automatically (Not recommended)
pip install mysql-connector-python<br>
pip install storage-local<br>
pip3 install python-dotenv<br>

# To support multiple environments
Documentation https://pypi.org/project/dotenv-cli/
pip install dotenv-cli

# Run the tests
We should have .env file in root directory of repo
cd .\tests\
python -m unittest test_filename.py .<br>

From root director<br>
python -m unittest .\tests\test_circles_storage.py<br>

from root directory
dotenv -f .\.env.play1 run python3 -m unittest .\tests\test_S3.py

# Trouble Shooting
## ModuleNotFoundError: No module named 'mysql'

# AWS Credentials needed
"s3:GetObject" which calls HeadObject API<br>
"s3:PutObject"<br>

# AWS Resouces
storage.us-east-1.play1.circ.zone	arn:aws:s3:::storage.us-east-1.play1.circ.zone/*<br>

# .env.play1
Please make sure you have in your .env.play1 all the variables from .env.example<br>

Please use ONLY CirclesStorage
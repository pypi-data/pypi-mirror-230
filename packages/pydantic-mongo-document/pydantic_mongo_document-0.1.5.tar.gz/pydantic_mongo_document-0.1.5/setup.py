# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pydantic_mongo_document']

package_data = \
{'': ['*']}

install_requires = \
['autoflake>=2.2.1,<3.0.0',
 'motor>=3.3.1,<4.0.0',
 'mypy>=1.5.1,<2.0.0',
 'pydantic>=2.3.0,<3.0.0']

setup_kwargs = {
    'name': 'pydantic-mongo-document',
    'version': '0.1.5',
    'description': 'Pydantic Async Mongo Document',
    'long_description': '# Pydantic Mongo Document\n\n`pydantic_mongo_document` is a Python library that provides a base class for creating MongoDB documents using Pydantic models.\n\n## Installation\n\nInstall the package using [pip](https://pip.pypa.io/en/stable/) or [poetry](https://python-poetry.org).\n\n### Using pip\n```bash\npip install pydantic_mongo_document\n```\n\n### Using poetry\n```bash\npoetry add pydantic_mongo_document\n```\n\nUsage\nTo use pydantic_mongo_document, you need to create a Pydantic model that represents your MongoDB document and inherit from the MongoDocument class provided by the library. Here\'s an example:\n\n```python3\nfrom pydantic_mongo_document import Document\n\nclass User(Document):\n    __collection__ = "users"\n    __database__ = "production"\n\n    name: str\n    email: str\n\n```\n\nIn this example, we define a User Pydantic Document model with two fields (name and email) and  \nspecifies the MongoDB collection name (users) and database name (production) using the `__collection__` and `__database__` class attributes.\n\n```python3\nfrom pydantic_mongo_document import Document\n\n# Set the MongoDB URI\nDocument.set_mongo_uri("mongodb://localhost:27017")\n\n\nclass User(Document):\n    __collection__ = "users"\n    __database__ = "production"\n\n    name: str\n    email: str\n\n\nasync def create_user():\n    user = User(name="John", email="john@example.com")\n\n    await user.insert()\n\n    user = await User.one(add_query={"name": "John"})\n    print(user) # User(id=ObjectId("64fc59cf6410868c9a40644b"), name="John", email="john@example")\n```\n\nIn this example, we created new User in database. We then used the `User.one` method to retrieve the user from the database.\n\n## Contributing\nPull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.\n\nPlease make sure to update tests as appropriate.\n\n## License\nMIT\n',
    'author': 'Yurzs',
    'author_email': 'yurzs@icloud.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)

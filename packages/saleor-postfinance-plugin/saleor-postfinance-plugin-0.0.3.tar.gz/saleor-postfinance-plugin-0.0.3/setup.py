import os
import re
from pathlib import Path

from setuptools import setup

long_description = (Path(__file__).parent / "README.md").read_text()

version = re.sub(
    r'^v',
    '',
    os.getenv('VERSION', 'v0.0.1')
)

setup(
    name="saleor-postfinance-plugin",
    version=version,
    description="Saleor PostFinance gateway plugin.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['saleor_postfinance_plugin'],
    install_requires=["postfinancecheckout==3.1.1"],
    license='MIT',
    url="https://github.com/significa/saleor-postfinance-plugin",
    keywords="saleor, saleor-plugin, saleor-gateway, saleor-gateway-plugin",
    author="Significa",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
    ],
    entry_points={
        "saleor.plugins": [
            (
                "saleor_postfinance_plugin="
                "saleor_postfinance_plugin.plugin:PostFinanceGatewayPlugin"
            )
        ]
    }
)

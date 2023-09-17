from setuptools import setup, find_packages

setup(
    name="hikari-discord-interactions",
    version="0.1.4",
    url="https://github.com/KeenanOH/hikari-discord-interactions/",
    author="KeenanOH",
    author_email="86394469+KeenanOH@users.noreply.github.com",
    description="A Discord interactions library built with hikari.",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    install_requires=["hikari[server]~=2.0.0.dev121"],
    python_requires=">=3.10",
)
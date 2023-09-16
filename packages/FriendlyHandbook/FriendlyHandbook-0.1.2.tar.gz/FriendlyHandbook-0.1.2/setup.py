from setuptools import setup, find_namespace_packages

setup(
    name="FriendlyHandbook",
    version="0.1.2",
    description="«FriendlyHandbook» - це корисна програма з інтерфейсом командного рядка, яка містить контактну книгу, нотатки, калькулятор та може аналізувати папки.",
    url="https://github.com/filinmbg/FriendlyHandbook",
    author="JustPython",
    author_email="filinmbg@gmail.com",
    license="MIT",
    packages=find_namespace_packages(),
    install_requires=["prompt-toolkit==3.0.39"],
    entry_points={
        "console_scripts": ["helloworld = FriendlyHandbook.main:assistant_bot"]
    },
)

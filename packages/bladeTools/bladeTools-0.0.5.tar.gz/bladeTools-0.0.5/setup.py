import setuptools

setuptools.setup(
    name="bladeTools",
    version="0.0.5",
    author="剑爆是十条街",
    author_email="author@example.com",
    description="A small example package",
    packages=setuptools.find_packages(),
    py_modules=['tools.io.file'],
    clean={"all": True}
)

from setuptools import _install_setup_requires, setup, find_packages

with open('README.md') as f:
  readme = f.read()

with open('LICENSE') as f:
  license = f.read()

setup(
  name='othello_rl',
  version='0.0.1',
  description='Package of creating othello AI for Minecraft datapack with reinforcement learning',
  long_description=readme,
  author='aka',
  install_requires=['matplotlib', 'NBT'],
  url='https://github.com/aka256/othello-rl',
  license=license,
  packages=find_packages(exclude=('tests', 'docs'))
)
from setuptools import setup

setup(name='Csgo-tm-api',
      version='0.0',
      description='Allows you to receive information from the https://market.csgo.com/',
      packages=['dist_cstm'],
      author_email='desynq@mail.ru',
      zip_safe=False,
      install_requires=['requests>=2.31.0'])
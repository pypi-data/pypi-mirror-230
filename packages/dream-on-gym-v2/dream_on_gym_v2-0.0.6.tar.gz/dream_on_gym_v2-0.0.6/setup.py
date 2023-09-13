from setuptools import setup, find_packages

setup_requires = ["wheel"]

setup(name='dream_on_gym_v2',
      version='0.0.6',
      description='',
      author='Hermann Ignacio Pempelfort Vergara',
      author_email='hermann.pempelfort@usm.cl',
      url='https://gitlab.com/IRO-Team/dream-on-gym-v2',
      packages=['dreamongymv2', 'dreamongymv2.gym_basic', 'dreamongymv2.gym_basic.envs', 'dreamongymv2.simNetPy', 'dreamongymv2.simNetPy.filemanager'],
      package_data={'dreamongymv2.simNetPy.filemanager' : ['bitRates.schema.json']},
      #packages=find_packages("src"),
      #package_dir={'': 'src'},
      #   install_requires=INSTALL_REQUIRES,
      include_package_data=True,
      install_requires=[
          "numpy",
          "jsonschema",
          "gymnasium",
          "importlib-metadata",
          "tensorflow == 2.12.0",
          "protobuf",
          "stable-baselines3[extra]",
          "mpi4py"
      ],
      )

from setuptools import setup
import os

def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as file:
        return file.read()
setup(
  name = 'game-simulator',         
  packages = ['game_simulator'],   
  version = '0.8',      
  license='MIT',        
  description = 'Creates simulations of any n*n game specified with payoff matrix',   
  long_description=read_file('README.md'),
  long_description_content_type='text/markdown',
  author = 'ankurtutlani',                   
  author_email = 'ankur.tutlani@gmail.com',      
  url = 'https://github.com/ankur-tutlani/game-simulator',   
  download_url = 'https://github.com/ankur-tutlani/game-simulator/archive/refs/tags/v_08.tar.gz',    
  keywords = ['game theory', 'evolutionary game', 'social norms','multi-agents','evolution','Nash equilibrium'],   
  install_requires=[            
          'numpy',
		  'pandas',
		  'setuptools',
		  'matplotlib'
		  
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      
    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
												
	'Programming Language :: Python :: 3.7',
  ],
)
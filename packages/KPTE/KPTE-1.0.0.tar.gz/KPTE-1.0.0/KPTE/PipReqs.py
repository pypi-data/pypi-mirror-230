import os
import shutil
import subprocess
import time


def Get(files):
    print('Generate a requirements.txt file >')

    print(f'pipreqs {files} --encoding=utf8')

    subprocess.Popen(f'pipreqs {files} --encoding=utf8')

    time.sleep(2)

    shutil.move(os.path.join(files, 'requirements.txt'), os.path.join(os.path.dirname(os.path.abspath(__file__)), 'requirements_copy.txt'))


def Move(OutputCodePath):
    shutil.move(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'requirements_copy.txt'), os.path.join(OutputCodePath, 'requirements.txt'))

    print('The enerate a requirements.txt file succeeded!')
    input('Please check the requirements.txt, if the dependent module is missing, please add: module name==module version at the end of the text, please press Enter after adding >>>')

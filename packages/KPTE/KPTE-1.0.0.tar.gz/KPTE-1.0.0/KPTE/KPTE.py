# -*- coding: utf-8 -*-

import argparse
import os
import subprocess
import os
import shutil
import py7zr
from KPTE import PipReqs

def KPTE():
    cmd_input = argparse.ArgumentParser(description='KaixinPyToExe helps:')
    cmd_input.add_argument('-p', '--path', type=str, metavar='', required=True, help='The path to the python file')
    cmd_input.add_argument('-o', '--output', type=str, metavar='', required=True, help='The path to the exe file')
    cmd_input.add_argument('-f', '--files', type=str, metavar='', required=True, help='Attach the files')
    cmd_input.add_argument('-n', '--name', type=str, metavar='', default='RUN', help='The file name')
    cmd_input.add_argument('-c', '--cmd', type=str, metavar='', default='c', help='The file name')
    cmd_input.add_argument('-i', '--icon', type=str, metavar='', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico'), help='The file icon')

    args = cmd_input.parse_args()

    OutputPythonPath = os.path.join(args.output, 'Python')
    OutputCodePath = os.path.join(args.output, 'Code')
    OutputWhlPath = os.path.join(args.output, 'WhlFiles')
    OutputExePath = args.output


    print(f'path:{args.path}  output:{args.output}  files:{args.files}')
    print('Start packing...')

    if not os.path.isdir(args.output) and not os.path.isfile(args.path):
        print('Path error.')
        print('Quit KaixinPyToExe.')
        os._exit()

    PipReqs.Get(args.files)


    print('Copy file >')

    src_folder = args.files
    dst_folder = os.path.dirname(os.path.abspath(__file__)) + '\\copy_'

    subprocess.call(['robocopy', src_folder, dst_folder, '/E'])

    shutil.move(os.path.dirname(os.path.abspath(__file__)) + '\\copy_', OutputCodePath)


    print('The copy succeeded!')


    print('Unzip >')
    print('Unzip >>> python files')

    archive = py7zr.SevenZipFile(f'{os.path.dirname(os.path.abspath(__file__))}\\Python.7z', mode='r')
    archive.extractall(path=OutputExePath)
    archive.close()

    print('The unzip succeeded!')

    PipReqs.Move(args.files)


    os.makedirs(OutputWhlPath)

    print('Pip >')

    drive, path = os.path.splitdrive(args.files)

    print(f'RunCmd: {OutputPythonPath}\\python.exe -m pip download -r {os.path.join(args.files, "requirements.txt")} -i https://pypi.tuna.tsinghua.edu.cn/simple -d {OutputWhlPath}')
    subprocess.run(f'{OutputPythonPath}\\python.exe -m pip download -r {os.path.join(args.files, "requirements.txt")} -i https://pypi.tuna.tsinghua.edu.cn/simple -d {OutputWhlPath}')


    print('Make Python File >')

    PyPath = os.path.join(OutputExePath, f'{args.name}.py')

    Code = f"""import os
import subprocess

files = r"{OutputExePath}"

drive, path = os.path.splitdrive(files)

Path = r"{args.files}"
subprocess.run(drive, shell=True)
subprocess.run(f'cd {{path}}', shell=True)
subprocess.run(fr'.\Python\python.exe -m pip install --no-index --find-links={{os.path.join(files, "WhlFiles")}} -r {{os.path.join(Path, "requirements.txt")}}', shell=True)

subprocess.run(f'.\Python\python.exe -u .\Code\{os.path.basename(args.path)}', shell=True)
"""

    with open(PyPath, 'w') as PyFile:
        PyFile.write(Code)

    print(f'MakeFile:\n{Code}')

    print('The make succeeded!')


    print('Pyinstaller >')

    DistDir = OutputExePath

    print(OutputExePath)
    print(DistDir)


    print(f'RunCmd: pyinstaller --icon={args.icon} -F -{args.cmd} --distpath={DistDir} {PyPath}')

    subprocess.Popen(f'pyinstaller --icon={args.icon} -F -{args.cmd} --distpath={DistDir} {PyPath}')

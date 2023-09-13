import argparse

import sys
import os
import shutil
from pathlib import Path
import fileinput
import platform
import stat

def replace_in_file(path:str, ori:str, replace:str):
    with fileinput.FileInput(path, inplace=True, backup='.bak') as file:
        for line in file:
            print(line.replace(ori, replace), end='')
    os.remove(path+'.bak')

def replace_in_dir(directory:str, ori:str, replace:str):
    files = os.listdir(directory)
    for file in files:
        cur_path = os.path.join(directory, file)
        if os.path.isdir(cur_path):
            replace_in_dir(cur_path, ori, replace)
        else:
            replace_in_file(cur_path, ori, replace)

def rm_error_handler(func, path, execinfo):
    os.chmod(path, stat.S_IWUSR)
    func(path)

def main():
    parser = argparse.ArgumentParser(
        description='Initialize c/c++ project.')

    parser.add_argument("project", help="the project name")
    parser.add_argument("-l", "--lib", action='store_true', help='this project is an library.')
    parser.add_argument('-m', '--modules', help='modules, split by ,')
    args = parser.parse_args()
    
    if 0 < len(os.listdir(os.getcwd())):
        print('Direcotry is not empty.Please clean it or change to an empty directory.')
        exit(-1)
    

    shutil.copytree(f'{os.path.dirname(__file__)}/cmake', 'cmake')
    shutil.copytree(f'{os.path.dirname(__file__)}/conan', 'conan')
    shutil.copyfile(f'{os.path.dirname(__file__)}/conanfile.txt.in', 'conanfile.txt.in')
    
    modules = []
    if args.modules:
        modules = args.modules.split(',')
    project:str = args.project
        
    root_cmake_file_content:str ='cmake_minimum_required(VERSION 3.8)\n'
    root_cmake_file_content += f'project({project})\n'
    root_cmake_file_content += '\n'
    
    root_cmake_file_content += 'include(cmake/config.cmake)\n'
    root_cmake_file_content += 'include(cmake/platform.cmake)\n'
    root_cmake_file_content += 'configure_file(${CMAKE_CURRENT_SOURCE_DIR}/conanfile.txt.in ${CMAKE_CURRENT_SOURCE_DIR}/conanfile.txt)\n'
    root_cmake_file_content += 'include(cmake/install_conan_deps.cmake)\n'
    root_cmake_file_content += '\n'
    
    
    if len(modules):
        for m in modules:
            m = m.strip()
            root_cmake_file_content += f'add_subdirectory({m})\n'
            inc_dir = f'{m}/include'
            if args.lib:
                inc_dir = f'{m}/include/project/{m}'

            os.makedirs(inc_dir, exist_ok=True)
            os.makedirs(f'{m}/src', exist_ok=True)
            Path(f'{inc_dir}/{m}.h').touch()
            Path(f'src/{m}.cxx').touch()
                
            with open(f'{m}/CMakeLists.txt', mode='w', encoding='utf-8') as cmake:
                cmake.write('include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)\n')
                cmake.write(f'file(GLOG_RECURSE {m.upper()}_PUB_HEADERS "{inc_dir}/*.h")\n')
                cmake.write(f'file(GLOB_RECURSE {m.upper()}_PRI_HEADERS "src/*.h")\n')
                cmake.write(f'file(GLOB_RECURSE {m.upper()}_SOURCES "src/*.cxx")\n')
                cmake.write('\n')
                cmake.write(f'add_library({m} ${{{m.upper()}_PUB_HEADERS}} ${{{m.upper()}_PRI_HEADERS}} ${{{m.upper()}_SOURCES}})')
    else:
        os.mkdir('include')
        os.mkdir('src')
        root_cmake_file_content += 'include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)\n'
        root_cmake_file_content += f'file(GLOB_RECURSE {project.upper()}_PUB_HEADERS  "include/*.h")\n'
        root_cmake_file_content += f'file(GLOB_RECURSE {project.upper()}_SOURCES "src/*.cxx")\n'
        root_cmake_file_content += f'file(GLOB_RECURSE {project.upper()}_PRI_HEADERS "src/*.h")\n'
        root_cmake_file_content += f'source_group("Pub Headers" FILES ${{{project.upper()}_PUB_HEADERS)}}\n'
        if args.lib:
            root_cmake_file_content += f'add_library({project.upper()}  ${{{project.upper()}_PUB_HEADERS}} ${{{project.upper()}_PRI_HEADERS}} ${{{project.upper()}_SOURCES}})'
        else:
            root_cmake_file_content += f'add_executable({project.upper()}  ${{{project.upper()}_PUB_HEADERS}} ${{{project.upper()}_PRI_HEADERS}} ${{{project.upper()}_SOURCES}})'
            
    with open('CMakeLists.txt', mode='w', encoding='utf-8') as cmake:
        cmake.write(root_cmake_file_content)
    

if __name__ == "__main__":
    sys.exit(main())
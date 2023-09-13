#!/usr/bin/env python

import argparse

import sys
import os
import shutil
from pathlib import Path
from .CppGenerator import OpenAPICppGenerator
import fileinput

def gen_cpp_sources(d:str, o:str, n:str, p:str)->str:
    test_section:str='# unit tests\n'
    for cur, subs, files in os.walk(d):
        for file in files:
            path = Path(cur).joinpath(file)
            try:
                generator = OpenAPICppGenerator(
                    doc= str(path),
                    output= o,
                    nsp= n,
                    project=p)
                
                generator.run()
                class_name = generator.get_main_class_name()
                test_section += f'add_executable({class_name}_test test/{class_name}Test.cxx)\n'
                test_section += f'target_link_libraries({class_name}_test  {p}_api {p}_api_core CONAN_PKG::Poco CONAN_PKG::googletest)\n'
                test_section += f'add_dependencies({class_name}_test {p}_api {p}_api_core)\n'
                test_section += f'set_target_properties({class_name}_test PROPERTIES FOLDER "tests")\n\n'
            except (OSError) as exception:
                print(exception)
                sys.exit(exception)
        for sub in subs:
            gen_cpp_sources(sub, o, n, p)

    return test_section

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

def gen_core_lib(output, namespace, project):
    core_dir = Path(os.path.dirname(__file__)).joinpath('core')
    shutil.copytree(core_dir, os.path.join(output, 'core'))
    
    os.rename(os.path.join(output, 'core', 'include', 'mlapi'), os.path.join(output, 'core', 'include', project))
    replace_in_dir(os.path.join(output, 'core'), '@PROJECT@', project)
    replace_in_dir(os.path.join(output, 'core'), '@NSP@', namespace)
    replace_in_dir(os.path.join(output, 'core'), '@API@', project.upper()+"_API")
    replace_in_dir(os.path.join(output, 'core'), '@api@', project.lower()+"_api")

def gen_cmake_file(output, namespace, project, tests:str):
    shutil.copy(os.path.join(os.path.dirname(__file__), 'tmpl', 'CMakeLists.txt'), os.path.join(output, 'CMakeLists.txt'))
    shutil.copy(os.path.join(os.path.dirname(__file__), 'tmpl', 'conanfile.txt'), os.path.join(output, 'conanfile.txt'))
    shutil.copytree(os.path.join(os.path.dirname(__file__), 'tmpl', 'cmake'), os.path.join(output, 'cmake'))
    
    replace_in_file(os.path.join(output, 'CMakeLists.txt'), '@PROJECT@', project)
    replace_in_file(os.path.join(output, 'CMakeLists.txt'), '@NSP@', namespace)
    replace_in_file(os.path.join(output, 'CMakeLists.txt'), '@API@', project.upper()+"_API")
    replace_in_file(os.path.join(output, 'CMakeLists.txt'), '@api@', project.lower()+"_api")
    replace_in_file(os.path.join(output, 'CMakeLists.txt'), '@TESTS_SECTION@', tests)

def main():
    parser = argparse.ArgumentParser(
        description='Generate cpp sources from OpenAPI document.')

    parser.add_argument("document_dir", help="special input OpenAPI document directory.")
    parser.add_argument("--output", help="special output directory.", default='out')
    parser.add_argument("--nsp", help="special namespace of all objects.", default='MindLinker')
    parser.add_argument("--project", help="special project name, if not, use 'mlapi'", default="mlapi")

    args = parser.parse_args()
    if os.path.exists(args.output):
        shutil.rmtree(args.output)
    gen_core_lib(args.output, args.nsp, args.project)
    test_section = gen_cpp_sources(args.document_dir, args.output, args.nsp, args.project)
    gen_cmake_file(args.output, args.nsp, args.project, test_section)

if __name__ == "__main__":
    sys.exit(main())

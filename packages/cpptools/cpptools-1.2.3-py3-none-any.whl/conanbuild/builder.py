import argparse

import sys
import os
import shutil
from pathlib import Path
import fileinput
import yaml
import platform
import stat

def get_os_name():
    osName=platform.system()
    if osName == 'Darwin':
        return 'Macos'
    else:
        return osName

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

def find_target(directory:str, target:str) ->bool:
    files = os.listdir(directory)
    for file in files:
        if file == target:
            return True

    return False

def install_native(target:str,  version:str, chn:str, compiler:str, compilerVersion:str, archs:list, debug:bool, addition_settings:str=''):
    osName=get_os_name()
    if osName == 'Windows':
        for arch in archs:
            cmd = f'conan install --build=missing --build={target}  -s os={osName} -s arch={arch} -s compiler="{compiler}" -s compiler.version={compilerVersion} -s compiler.runtime=MD -s build_type=Release {addition_settings}  {target}/{version}@1602/{chn}'
            print(cmd)    
            assert 0 == os.system(cmd)
            if debug:
                cmd=f'conan install --build=missing --build={target} -s os={osName} -s arch={arch} -s compiler="{compiler}" -s compiler.version={compilerVersion} -s compiler.runtime=MDd -s build_type=Debug {addition_settings}   {target}/{version}@1602/{chn}'
                print(cmd)    
                assert 0 == os.system(cmd)
    else:
        for arch in archs:
            cmd=f'conan install --build=missing --build={target} -s os={osName} -s arch={arch} -s compiler="{compiler}" -s compiler.version={compilerVersion} -s build_type=Release {addition_settings} {target}/{version}@1602/{chn}'
            print(cmd)    
            assert 0 == os.system(cmd)
            if debug:
                cmd=f'conan install --build=missing --build={target} -s os={osName} -s arch={arch} -s compiler="{compiler}" -s compiler.version={compilerVersion} -s build_type=Debug {addition_settings}  {target}/{version}@1602/{chn}'
                print(cmd)    
                assert 0 == os.system(cmd)
                
def install_android(target:str, version:str, chn:str, compiler:str, compilerVersion:str, archs:list, api_level:str, debug:bool, addition_settings:str=''):
    for arch in archs:
        cmd=f'conan install --build=missing --build={target}  -s os=Android -s arch={arch} -s compiler="{compiler}" -s compiler.version={compilerVersion} -s os.api_level={api_level} -s build_type=Release {addition_settings}  {target}/{version}@1602/{chn}'
        print(cmd)    
        assert 0 == os.system(cmd)
        if debug:
            cmd=f'conan install --build=missing --build={target} -s os=Android -s arch={arch} -s compiler="{compiler}" -s compiler.version={compilerVersion} -s os.api_level={api_level} -s build_type=Debug {addition_settings}  {target}/{version}@1602/{chn}'
            print(cmd)    
            assert 0 == os.system(cmd)
            
def install_ios(target:str, version:str, chn:str, compiler:str, compilerVersion:str, archs:list, debug:bool, addition_settings:str=''):
    for arch in archs:
        cmd=f'conan install --build=missing --build={target} -s os=iOS -s arch={arch} -s compiler={compiler} -s compiler.version={compilerVersion} -s build_type=Release {addition_settings}  {target}/{version}@1602/{chn}'
        print(cmd)    
        assert 0 == os.system(cmd)
        if debug:
            cmd=f'conan install --build=missing --build={target} -s os=iOS -s arch={arch} -s compiler={compiler} -s compiler.version={compilerVersion} -s build_type=Debug {addition_settings}  {target}/{version}@1602/{chn}'
            print(cmd)    
            assert 0 == os.system(cmd)

def build_native(conanfile:str, chn:str, compiler:str, compilerVersion:str, archs:list, debug:bool, addition_settings:str=''):
    osName=get_os_name()
    if osName == 'Windows':
        for arch in archs:
            cmd = f'conan create -s os={osName} -s arch={arch} -s compiler="{compiler}" -s compiler.version={compilerVersion} -s compiler.runtime=MD -s build_type=Release {addition_settings}  {conanfile} 1602/{chn}'
            print(cmd)    
            assert 0 == os.system(cmd)
            if debug:
                cmd=f'conan create -s os={osName} -s arch={arch} -s compiler="{compiler}" -s compiler.version={compilerVersion} -s compiler.runtime=MDd -s build_type=Debug {addition_settings}   {conanfile} 1602/{chn}'
                print(cmd)    
                assert 0 == os.system(cmd)
    else:
        for arch in archs:
            cmd=f'conan create -s os={osName} -s arch={arch} -s compiler="{compiler}" -s compiler.version={compilerVersion} -s build_type=Release {addition_settings}  {conanfile} 1602/{chn}'
            print(cmd)    
            assert 0 == os.system(cmd)
            if debug:
                cmd=f'conan create -s os={osName} -s arch={arch} -s compiler="{compiler}" -s compiler.version={compilerVersion} -s build_type=Debug {addition_settings}  {conanfile} 1602/{chn}'
                print(cmd)    
                assert 0 == os.system(cmd)

def build_android(conanfile:str, chn:str, compiler:str, compilerVersion:str, archs:list, api_level:str, debug:bool, addition_settings:str=''):
    for arch in archs:
        cmd=f'conan create -s os=Android -s arch={arch} -s compiler="{compiler}" -s compiler.version={compilerVersion} -s os.api_level={api_level} -s build_type=Release {addition_settings}  {conanfile} 1602/{chn}'
        print(cmd)    
        assert 0 == os.system(cmd)
        if debug:
            cmd=f'conan create -s os=Android -s arch={arch} -s compiler="{compiler}" -s compiler.version={compilerVersion} -s os.api_level={api_level} -s build_type=Debug {addition_settings}  {conanfile} 1602/{chn}'
            print(cmd)    
            assert 0 == os.system(cmd)
    
def build_ios(conanfile:str, chn:str, compiler:str, compilerVersion:str, archs:list, debug:bool, addition_settings:str=''):
    for arch in archs:
        cmd=f'conan create -s os=iOS -s arch={arch} -s compiler={compiler} -s compiler.version={compilerVersion} -s build_type=Release {addition_settings}  {conanfile} 1602/{chn}'
        print(cmd)    
        assert 0 == os.system(cmd)
        if debug:
            cmd=f'conan create -s os=iOS -s arch={arch} -s compiler={compiler} -s compiler.version={compilerVersion} -s build_type=Debug {addition_settings}  {conanfile} 1602/{chn}'
            print(cmd)    
            assert 0 == os.system(cmd)

def rm_error_handler(func, path, execinfo):
    os.chmod(path, stat.S_IWUSR)
    func(path)

def read_target_name(file:str)->str:
    f = open(file, 'r', encoding='utf-8')
    for line in f.readlines():
        l = line.replace(' ', '')
        l = l.replace('\t', '')
        if l.startswith('name='):
            return l.removeprefix('name=')

    return None

def read_target_version(file:str)->str:
    f = open(file, 'r', encoding='utf-8')
    for line in f.readlines():
        l = line.replace(' ', '')
        l = l.replace('\t', '')
        if l.startswith('version='):
            return l.removeprefix('version=')

    return None

def run():
    if not os.path.exists(f'{os.path.expanduser("~")}/.cpptools/conan_targets'):
        shutil.copytree(f'{os.path.dirname(__file__)}/targets', f'{os.path.expanduser("~")}/.cpptools/conan_targets')
    
    parser = argparse.ArgumentParser(
        description='Generate project files of MaxME based platform etc.')

    parser.add_argument("target", help="the target project name.special an predefined project name or an 'conanfile.py.in'")
    parser.add_argument("-t", "--tag", help="the git tag of target, if specified,  use 'stable' conan channel and use 'tag' as version")
    parser.add_argument("-b","--branch", help="the git branch of target, if specified, use 'branch' as conan channel")
    parser.add_argument("-r", "--ref", help="the git ref identify of target, if specified, use 'dev' as conan chanel and use 'ref' as version")
    parser.add_argument('-v','--version', help='the conan package version, if specified will override default.')
    parser.add_argument('-d', '--default', help='force use default rule to build package. if not set this option, we first use "${user_dir}/.cpptools/conan_targets" as conanbuild configurations.', action='store_true')
    parser.add_argument('--without_native', action='store_true', help='not build native package')
    parser.add_argument('--android', action='store_true', help='build android package.')
    if get_os_name() == 'Macos':
        parser.add_argument('--ios', action='store_true', help='build ios package.')
    parser.add_argument('--arch', choices=['x86','x86_64','armv7','armv8','all', 'default'], default='default', help='target arch')
    parser.add_argument('--android_arch', choices=['x86','x86_64','armv7','armv8','all', 'default'], default='default', help='android target arch')
    parser.add_argument('--debug', action='store_true', help='build debug package.')
    parser.add_argument('--compiler', choices=['gcc','clang', 'apple-clang', 'Visual Studio'], help='the compiler')
    parser.add_argument('--android_compiler', choices=['gcc', 'clang'], help='the android NDK compiler')
    parser.add_argument('--android_compiler_version', help='the android compiler version')
    parser.add_argument('--android_api_level', help='the android API level')
    parser.add_argument('--compiler_version', help='the version of compiler')
    parser.add_argument('--upload', action='store_true', help='upload pacakge to conan recip', default=False)
    parser.add_argument('-c', '--chn', help='specify conan channel, will override default rule.')
    parser.add_argument('-s', '--settings', help='specify additional conan settings.', default='')
    parser.add_argument('-e', '--env', help='specify addtional envrioment variables.')
    parser.add_argument('--build_version', help='append building number to version, avalible with CI system.')
    parser.add_argument('-i', '--install', action='store_true', help='build with install package from remote recip.')

    args = parser.parse_args()
    targets_dir = f'{os.path.expanduser("~")}/.cpptools/conan_targets'
    if args.default:
        targets_dir = f'{os.path.dirname(__file__)}/targets'

    if args.target == 'list':
        print('inside pacakges:\n')
        refs = os.listdir(targets_dir)
        for ref in refs:
            if ref.endswith('.py.in'):
                print(ref.removesuffix(".py.in"))
        exit(0)

    git_ref = ''
    version = ''
    git_checkout=''
    chn = 'dev'
    compiler = args.compiler
    compiler_version = args.compiler_version
    archs = []
    android_archs = []
    target = args.target
    install = args.install
    
    conan_file = f'{os.path.dirname(__file__)}/conanfile.py'
    if os.path.exists(conan_file) :
        if os.path.isdir(conan_file):
            shutil.rmtree(conan_file)
        else:
            os.remove(Path(conan_file))

    reposes_config = open(f'{targets_dir}/repos.yaml', "r", encoding='utf-8')
    reposes = yaml.load(reposes_config, Loader=yaml.Loader)

    tmpl_file:str = args.target
    
    if not Path(tmpl_file).is_file() :
        if find_target(targets_dir, f'{tmpl_file}.py.in'):
            tmpl_file = f'{targets_dir}/{tmpl_file}.py.in'
        else:
            print('Not predefiend target. Will try install with build from remote recips.')
            install = True
    else:
        target = read_target_name(tmpl_file)
        version = read_target_version(tmpl_file)

    osName=get_os_name()
    if (not compiler) or len(compiler) == 0 :
        if osName == 'Windows':
            compiler='Visual Studio'
        elif osName == 'Macos':
            compiler='clang'
        else :
            compiler='gcc'
    if (not compiler_version) or len(compiler_version) == 0 :
        if compiler == 'Visual Studio':
            compiler_version= '15'
        elif compiler == 'clang':
            compiler_version= '10'
        elif compiler == 'gcc':
            ver = os.popen('gcc -dumpversion')
            compiler_version= ver.read().strip()
            if compiler_version.count('.') > 1:
                compiler_version = compiler_version[:compiler_version.rfind('.')]
            
    if args.arch == 'all':            
        if osName == 'Windows':
            archs.append('x86')
            archs.append('x86_64')
        else :
            archs.append('x86')
            archs.append('x86_64')
            archs.append('armv7')
            archs.append('armv8')
    elif args.arch == 'default':
        if osName == 'Windows':
            archs.append('x86')
            archs.append('x86_64')
        else :
            archs.append('x86_64')
    else:
        archs.append(args.arch)    
        
        
    if args.android_arch == 'all':            
        android_archs.append('x86')
        android_archs.append('x86_64')
        android_archs.append('armv7')
        android_archs.append('armv8')
    elif args.android_arch == 'default':
        android_archs.append('armv7')
        android_archs.append('armv8')
    else:
        archs.append(args.arch)  
    
    android_compiler = None
    android_compiler_version = None
    android_api_level = None
    
    if args.android_compiler:
        android_compiler = args.android_compiler.strip()   
    if args.android_compiler_version:
        android_compiler_version = args.android_compiler_version.strip()
    if args.android_api_level:
        android_api_level = args.android_api_level
    if not android_compiler or len(android_compiler) == 0:
        android_compiler = 'gcc'
    
    if not android_compiler_version or len(android_compiler_version) == 0:
        if 'gcc' == android_compiler:
            android_compiler_version = '4.9'
        else:
            android_compiler_version = '14'
    
    if not android_api_level or len(android_api_level) == 0:
        android_api_level = '21'

    if args.tag :
        git_ref = args.tag.strip()
        version = args.tag.strip()
        chn = 'stable'
    elif args.ref :
        git_ref = args.ref.strip()
        version = args.ref.strip()
        git_checkout = f'self.run("git checkout {args.ref.strip()}")'
    elif args.branch :
        git_ref = args.branch.strip()
        chn = args.branch.strip()
        
    if args.version:
        version = args.version.strip()
    
    if len(version) == 0:
        repos = reposes[args.target]
        if not repos:
            Warning('not detected version.')
        else:
            os.system(f'git clone {repos} -b {args.branch} src')
            os.chdir('src')
            version = os.popen('git rev-parse --short HEAD').read()
            version = version.replace('\n', '')
            os.chdir('..')
            os.system('rm -fr src')

    if args.chn:
        chn = args.chn.strip()
    if args.build_version:
        version += f'.{args.build_version}'.strip()

    if args.env:
        envs = args.env.split(',')
        for env in envs:
            kv = env.split('=')
            if len(kv) == 2:
                os.putenv(kv[0], kv[1]) 
    
    if install:    
        os.system(f'conan remove --locks')
        os.system(f'conan remove {target}/{version}@1602/{chn} -f -s')
    else:
        shutil.copyfile(tmpl_file, conan_file)
        replace_in_file(conan_file, '@checkout@', git_checkout)
        if len(git_checkout) >0:
            replace_in_file(conan_file, '@git_ref@', '')
        else:
            replace_in_file(conan_file, '@git_ref@', f'-b {git_ref}')
        if len(version) >0 :
            replace_in_file(conan_file, '@version@', version)

    if not args.without_native:
        if install:
            install_native(target, version, chn, compiler, compiler_version, archs, args.debug, args.settings)
        else:
            build_native(conan_file, chn, compiler, compiler_version, archs, args.debug, args.settings)
    if args.android:
        android_compiler = android_compiler.strip()
        android_compiler_version = android_compiler_version.strip()
        android_api_level = android_api_level.strip()
        if install:
            install_android(target, version, chn, android_compiler, android_compiler_version, android_archs, android_api_level, args.debug, args.settings)
        else:
            build_android(conan_file, chn, android_compiler, android_compiler_version, android_archs, android_api_level, args.debug, args.settings)
    if get_os_name() == 'Macos':
        if args.ios:
            if install:
                install_ios(target, version, chn, compiler, compiler_version, archs, args.debug, args.settings)
            else:
                build_ios(conan_file, chn, compiler, compiler_version, archs, args.debug, args.settings)

    if args.upload:
        assert 0 == os.system(f'conan upload {target}/{version}@1602/{chn} --all --force')

if __name__ == "__main__":
    sys.exit(run())
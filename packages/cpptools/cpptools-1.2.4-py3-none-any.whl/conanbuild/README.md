# 关于CONAN-BUILDER

conan-builder是一个提供参数化构建conan package的工具，其主要设计目标包括：
* 提供对各个项目conanfile统一管理的能力
* 提供一套版本号命名、conan通道命名方式的规范，但在必要的时候可以明确指定
* 通过参数化的支持，达到配置一个CI项目，就可以构建所有conan pacakge的目标，减少CI项目的配置维护工作

## 工作原理
conan-builder支持构建两种类型的项目：
1. 提供标准conanfile的项目
2. 提供参数化conanfile模板项目
3. 重新构建已经存储在conan recip中的软件包

当使用第一种方式时，conan-builder从conanfile中读取[`name`, `version`]字段用于`conan upload`命令，随后分别调用`conan create`和`conan upload`完成构建和上传。

当使用第二种方式时，conan-builder从输入中读取相关参数，根据指定的模板文件，渲染出`conanfile.py`文件，然后分别调用`conan create`和`conan upload`完成构建和上传。目前，**约定将所有的模板文件保存在conan-builder项目下的`target`目录，并以`${target}.py.in`的方式命名**。
<br>
### 参数说明
当使用第二种方式时，以下参数化的属性，将会被渲染到可用于`conan create`命令的标准conanfile文件中：

* 源代码引用，提供`--tag``--branch``--ref`三个命令行参数，分别用于指定源码仓库的tag、branch和commit id。

* 版本号，可以在命令行参数中明确的指定，否则将按照以下规则确定（按优先级排序）：
    * 如果指定了源码的tag，将以tag作为版本号。隐藏的意思是tag应该以版本号命名
    * 如果指定了git commit id，将以commit id作为版本号
    * 如果指定git branch，将以改分支`HEAD`的commit id作为版本号

<br>
而以下参数化属性，在两种方式下都可使用，被用于`conan create`和`conan upload`命令中：

* conan通道，如果未在命令行参数中明确指定，将按照以下规则确定（按优先级排序）：
    * 如果指定了源码的tag,将使用'stable'通道。意味着这是一个稳定的版本。
    * 如果指定了git commit id，将使用'dev'通道
    * 如果指定branch，将使用以branch名称命名的通道

* 编译器，如果未明确指定，conan-builder将根据目标host自动确定
    * Windows将使用`Visual Studio`
    * Linux将使用`gcc`
    * OSX将使用`clang`

* 编译器版本，如果未明确指定，将自动确定：
    * Visual Studio 将使用15（2017）
    * gcc将使用4.9
    * clang将使用10.1
* 目标处理器架构，如果未明确指定：
    * Windows将构建`x86`、`x86_64`
    * 其它平台将构建`x86`、`x86_64`、`armv7`、`armv8`

### 如何重新构建已经存储于recip中的软件包
以下两种情况，会尝试“重新构建”：
* targets目录下没有该软件包的conanfile模板
* 传入`-i`或者 `--install`选项

同时需要通过`-c`制定conan通道和通过`--version`指定版本号以形成一个完整的reference。
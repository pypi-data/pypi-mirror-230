#!/usr/bin/env python

from pathlib import Path
from logging import error
from io import TextIOWrapper
from faker import Faker

import json
import os
import fileinput
import shutil

import yaml

class OpenAPICppGenerator:
    document : str = None
    output = Path("out")
    namespace : str = None
    project: str = 'mlapi'
    
    __common_header_comment : str = ""
    __doc : dict = None

    __interface_header:TextIOWrapper = None
    __data_header:TextIOWrapper = None
    __impl_header:TextIOWrapper = None
    __impl_source:TextIOWrapper = None
    __main_class_name:str = None

    def get_main_class_name(self)->str:
        """_summary_

        Returns:
            str: _description_
        """
        return self.__main_class_name

    def __init__(self, doc, output, nsp, project) -> None:
        self.document = doc
        if output:
            self.output = Path(output)
        if not self.output.is_absolute():
            self.output.absolute()
            
        self.namespace = nsp
        self.project = project

    def run(self) -> None:
        """start to generate cpp files.
        """
        file = open(self.document, "r", encoding='utf-8')
        self.__doc = yaml.load(file, Loader=yaml.Loader)

        if not self.__doc.get('openapi'):
            error("invalid openapi document : 'openapi' missing.")
        if not self.__doc.get("info"):
            error("Invalid OpenAPI document : 'info' missing.")
        if not self.__doc.get("paths"):
            error("Invalid OpenAPI document : 'paths' missing.")

        self.output.mkdir(parents=True, exist_ok=True)
        include_dir = self.output.joinpath("include", self.project)
        src_dir = self.output.joinpath("src")
        include_dir.mkdir(parents=True, exist_ok=True)
        src_dir.mkdir(parents=True, exist_ok=True)

        self.__parse_common_header_comment(self.__doc.get("info"))

        name_and_type= Path(self.document).name.split(".")
        self.__main_class_name= name_and_type[0]
        self.__data_header = open(include_dir.joinpath(self.__main_class_name +"Datas.h"), "w", encoding="utf-8")
        self.__interface_header = open(include_dir.joinpath(self.__main_class_name + ".h"), "w", encoding="utf-8")
        self.__impl_header = open(src_dir.joinpath(self.__main_class_name + "Impl.h"), "w", encoding="utf-8")
        self.__impl_source = open(src_dir.joinpath(self.__main_class_name +"Impl.cxx"), "w", encoding="utf-8")

        schemas = self.__scan_schemas()
        
        self.__gen_schemas_declaration(schemas, self.__data_header)
        self.__gen_interface_header()
        self.__gen_impl_header()
        self.__gen_impl_source_file()


        if self.namespace:
            self.__impl_header.write("}//namespace "  + self.namespace + "\n")
            self.__interface_header.write("}//namespace "  + self.namespace + "\n")
            self.__impl_source.write("}//namespace "  + self.namespace + "\n")

        self.__gen_test_source()

        self.__impl_header.close()
        self.__data_header.close()
        self.__interface_header.close()
        self.__impl_source.close()

    def __scan_schema(self, schema : dict, ret_schemas:list, name:str='', file:str=''):
        ref:str = schema.get('$ref')
        schema_type:str = schema.get('type')
        
        if ref:
            if not ref.startswith('#'):
                s = schema.copy()
                path_list = ref.split('/')
                name = path_list[len(path_list) - 1].removesuffix('.yaml').removesuffix('.json')
                s.setdefault('x-name', name)
                if s not in ret_schemas:
                    ret_schemas.append(s)
                    if len(file) == 0:
                        ref_file = str(Path(self.document.removesuffix(Path(self.document).name)).joinpath(ref).absolute())
                    else:
                        ref_file = str(Path(file.removesuffix(Path(file).name)).joinpath(ref).absolute())
                    s.setdefault('x-file', ref_file)
            else:
                s = self.__get_object_from_path(ref)
                self.__scan_schema(s, ret_schemas, ref[(ref.rfind('/')+1):], file)
        
        if schema_type == 'array':
            items_schema = schema.get('items')
            if items_schema:
                self.__scan_schema(items_schema, ret_schemas, name + 'Item')
            s = schema.copy()
            s.setdefault('x-name', name)
            if s not in ret_schemas:
                ret_schemas.append(s)
        elif schema_type == 'object':     
            properties:dict = schema.get('properties')
            if not properties:
                return
            
            for prop, prop_schema in properties.items():
                prop_type:str = prop_schema.get('type') 
                if prop_type=='object':
                    self.__scan_schema(prop_schema, ret_schemas, name+prop.title(), file)
                if prop_type == 'array':
                    self.__scan_schema(prop_schema, ret_schemas, name + prop.title(), file)
                if prop_schema.get('$ref'):
                    self.__scan_schema(prop_schema, ret_schemas, prop.title(), file)
            
            s = schema.copy()
            s.setdefault('x-name', name)
            if s not in ret_schemas:
                index = 0
                for ret_schemas_item in ret_schemas:
                    ps = ret_schemas_item.get('properties')
                    if ps:
                        for n, p in ps.items():
                            r = p.get('$ref')
                            if r and name == r[r.rfind('/')+1:]:
                                break
                            index += 1
                if index < len(ret_schemas):
                    ret_schemas.insert(index, s)
                else:
                    ret_schemas.append(s)
                    
    def __scan_operation(self, operation : dict, ret_schemas:list):
        parameters:list = operation.get('parameters')
        body = operation.get('requestBody')
        responses = operation.get('responses')
        operation_name:str = operation.get('operationId')

        if body:
            if body.get('content'):
                m = body.get('content').get('application/json')
                if not m:
                    m = body.get('content').get("'*/*'")
                if m and m.get('schema'):
                    schema = m.get('schema')
                    self.__scan_schema(schema, ret_schemas, operation_name+'Body')

        if parameters:
            for parameter in parameters:
                schema = parameter.get('schema')
                if not schema:
                    continue
                self.__scan_schema(schema, ret_schemas, parameter.get('name'))

        for code, response in responses.items():
            c = response.get('content')
            if not c:
                continue
            m = c.get('application/json')
            if not m:
                m = c.get("'*/*'")
            if m and m.get('schema'):
                schema = m.get('schema')
                self.__scan_schema(schema, ret_schemas, operation_name + 'Response' + code)

    def __scan_schemas(self) -> list:
        ret_schemas : list = []
        
        operation_schemas : list = []
        paths:dict = self.__doc.get("paths")
        for path_item in paths.values():
            if path_item.get('$ref'):
                Warning('now, not support outside path item difinitions.')
            else:
                path_params = path_item.get('parameters')
                if path_params:
                    for param in path_params:
                        if param.get('$ref'):
                            continue
                        param_schema = param.get('schema')
                        if param_schema:
                            self.__scan_schema(param_schema, ret_schemas, param.get('name'))
                            
                ops = ['get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace']
                for operation in ops:
                    if path_item.get(operation):
                        self.__scan_operation(path_item.get(operation), operation_schemas)

        for schema in operation_schemas:
            ret_schemas.append(schema) 
            
        components:dict = self.__doc.get("components") 
        if components:
            schemas:dict = components.get("schemas")
            request_bodies:dict = components.get("requestBodies")
            responses:dict = components.get("responses")
            parameters:dict = components.get("paramerters")
            headers:dict = components.get("headers")

            if request_bodies:
                for name, body in request_bodies.items():
                    m = body.get('content').get('application/json')
                    if not m:
                        m = body.get('content').get("'*/*'")
                    if m and m.get('schema'):
                        schema = m.get('schema')
                        self.__scan_schema(schema, ret_schemas, name)
                        
            if responses:        
                for name, response in responses.items():
                    c = response.get('content')
                    if not c:
                        continue
                    m = c.get('application/json')
                    if not m :
                        m = c.get("'*/*'")
                    if m and m.get('schema'):
                        schema = m.get('schema')
                        self.__scan_schema(schema, ret_schemas, name)

            if headers:
                for name, header in headers.items():
                    schema = header.get('schema')
                    if schema:
                        self.__scan_schema(schema, ret_schemas, name)
                        
            if parameters:
                for name, parameter in parameters.items():
                    schema = parameter.get('schema')
                    if schema:
                        self.__scan_schema(schema, ret_schemas, name)

            if schemas:
                for name, schema in schemas.items():
                    self.__scan_schema(schema, ret_schemas, name)

        return ret_schemas
        
    def __parse_common_header_comment(self, info) -> None:
        """Parse common comment for headers.   
        Args:
            info (OpenAPI Info Object): https://openapi.apifox.cn/#info-%E5%AF%B9%E8%B1%A1
        """
        if not info.get("title"):
            error("Invalid 'info' : 'title' missing.")
        if not info.get("version"):
            error("Invalid 'info': 'version' missing.")

        self.__common_header_comment += "/**\n"
        self.__common_header_comment += info.get("title") +"\n"
        if info.get("description"):
            self.__common_header_comment += info.get("description") + "\n"
        if info.get("termsOfService"):
            self.__common_header_comment += "Terms of service: "
            self.__common_header_comment += info.get("termsOfService") + "\n"
        if info.get("contact"):
            self.__common_header_comment += self.__get_contact_string(info.get("contact"))
            self.__common_header_comment += "\n"
        if hasattr(info, "license"):
            self.__common_header_comment += self.__get_license_string(info.get("license"))
            self.__common_header_comment += "\n"
        self.__common_header_comment += "**/\n"

    def __get_contact_string(self, contact:dict) -> str:
        coantact_string = ""
        for key, value in contact:
            coantact_string += key + " :" + value + "\n"
        return coantact_string    

    def __get_license_string(self, license_object:dict) -> str:
        license_string = "License:"
        license_string += license_object.get("name")
        license_string += " "
        license_string += license_object.get("url")
        license_string += "\n"
        return license_string

    def __gen_interface_header(self) ->None:  
        self.__interface_header.write(self.__common_header_comment)
        self.__interface_header.write("#pragma once \n")
        self.__interface_header.write("#include <cstdint>\n")
        self.__interface_header.write("#include <string>\n")
        self.__interface_header.write("#include <vector>\n")
        self.__interface_header.write("#include <memory>\n")
        self.__interface_header.write("#include <functional>\n")
        self.__interface_header.write("#include \""+ self.project + "/" + self.__main_class_name +"Datas.h\"\n")
        self.__interface_header.write(f'#include "{self.project}/core/ApiCore.h"\n')
        self.__interface_header.write("\n")
        
        if self.namespace:
            self.__interface_header.write("namespace " + self.namespace + "\n")
            self.__interface_header.write("{\n")
        self.__interface_header.write("class " + self.__main_class_name + "\n")
        self.__interface_header.write("{\n")
        self.__interface_header.write("public:\n")
        
        self.__interface_header.write("  static std::string version()\n")
        self.__interface_header.write("  {\n")
        self.__interface_header.write("    return \"" + self.__doc.get("info").get("version") + "\";\n")
        self.__interface_header.write("  }\n")

        self.__interface_header.write("  virtual void setServer(const std::string& server) = 0;\n\n")

        for path, item in self.__doc.get("paths").items():
            self.__interface_header.write("  // @group " + path + "\n\n")
            self.__write_methods_declaration(self.__interface_header, item)
            self.__interface_header.write("\n")
                
        self.__interface_header.write("};\n")

        self.__interface_header.write(f'{self.__main_class_name}* {self.project.upper()}_API create{self.__main_class_name}(std::shared_ptr<ApiCore> core);\n')

    def __get_object_from_path(self, path:str):
        locations = path.removeprefix("#/").split(sep="/")   
        obj = self.__doc
        for location in locations:
            obj = obj.get(location)
            if not obj:
                return None
        if obj == self.__doc:
            return None
        return obj

    def __write_methods_declaration(self, header:TextIOWrapper, item:dict, impl=False):
        ref:str = item.get("$ref")
        if ref:
            if ref.startswith("#"):
                error("Invalid reference : " + ref)
            else:
                if ref.endswith(".yaml"):
                    stream = open(ref, "r", encoding="utf-8")
                    ref_item = yaml.load(stream, yaml.Loader)
                    self.__write_methods_declaration(header, ref_item, impl)
                elif ref.endswith(".json"):
                    stream = open(ref, "r", encoding="utf-8")
                    ref_item = json.load(stream)
                    self.__write_methods_declaration(header, ref_item, impl)
                else:
                    error("only support yaml or json reference.")    
        else:
            item_params = {}
            if item.get("parameters"):
                item_params = self.__parameters_vec_to_dict(item.get("parameters"))
            if item.get("get"):
                self.__write_operation_declaration(header, item.get("get"), item_params, impl)
            if item.get("put"):
                self.__write_operation_declaration(header, item.get("put"), item_params, impl)
            if item.get("post"):
                self.__write_operation_declaration(header, item.get("post"), item_params, impl)
            if item.get("delete"):
                self.__write_operation_declaration(header, item.get("delete"), item_params, impl)
            if item.get("options"):
                self.__write_operation_declaration(header, item.get("options"), item_params, impl)
            if item.get("head"):
                self.__write_operation_declaration(header, item.get("head"), item_params, impl)
            if item.get("patch"):
                self.__write_operation_declaration(header, item.get("patch"), item_params, impl)
            if item.get("trace"):
                self.__write_operation_declaration(header, item.get("trace"), item_params, impl)

    def __write_operation_declaration(self, header:TextIOWrapper, operation:dict, path_params:dict, impl=False):        
        header.write("  /**\n")
        header.write("  " + operation.get("operationId"))
        header.write("\n")
        if operation.get("deprecated"):
            header.write("  @deprecated \n")
        if operation.get("summary"):
            header.write("  " + operation.get("summary"))
            header.write("\n")
        if operation.get("description"):
            header.write("  @desc ")
            header.write("    " + operation.get("description"))
            header.write("\n")
        header.write("  Responses: \n")
        rsps : dict = operation.get("responses")
        for code, rsp in rsps.items():
            header.write("  " + code.ljust(36))
            header.write(rsp.get("description") + "  ")
            header.write("@see ")
            if self.namespace:
                header.write(self.namespace + "::")
            content = rsp.get("content")
            if not content:
                continue
            if content.get("application/json"):
                schema =  content.get("application/json").get("schema")
            else :
                schema =  content.get("*/*").get("schema")
            if schema.get("$ref"):
                ref = schema.get("$ref") 
                ref_list :list = ref.split('/')
                name:str = ref_list[len(ref_list) - 1]
                name = name.removesuffix('.yaml')
                name = name.removeprefix('.json')
                
                header.write(name + "\n")
            else:
                name = operation.get("operationId") + "Response" + code
                header.write(name + "\n")
        if operation.get("tags"):
            header.write("  @tag ")
            for tag in operation.get('tags'):
                header.write(tag + " ")
            header.write("\n")
        header.write("  */\n")
            
        header.write("  virtual int " + operation.get("operationId") + "(")
        params = self.__merge_operation_parameters(path_params, operation)
        self.__write_function_args(header, operation.get("operationId"),  params, operation.get("requestBody"))
        
        if impl:
            header.write(" ) override;")
        else:
            header.write(" ) = 0;")
        header.write("\n\n")

    def __merge_operation_parameters(self, path_params : dict, operation:dict)-> dict:
        params = path_params.copy()
        if operation.get("parameters"):
            operation_params:dict = self.__parameters_vec_to_dict(operation.get("parameters"))
            for n, p in operation_params.items():
                params[n] = p
        return params
        
    def __write_function_args(self, ios:TextIOWrapper,  operation_id:str, params:dict, request_body:dict=None)->None:
        for p in params.values():
            name:str = p.get("name")
            ios.write(" ")
            schema = p.get("schema")
            ios.write(self.__get_cpp_type_from_json_schema(schema))
            ios.write(" ")
            ios.write(name)
            ios.write(",")
            
        if request_body:
            content:dict = request_body.get("content")
            ref:str = None
            body_schema:dict = None
            if content:
                # only support application/json, and should special schema.
                if content.get("application/json"):
                    body_schema = content.get("application/json").get("schema")
                else:
                    body_schema = content.get("'*/*'").get("schema")
                ref = body_schema.get("$ref")  
            else:
                ref = request_body.get("$ref")
                
            if ref:
                type_name = ref.split("/")
                ios.write(" const ")
                ios.write(type_name[len(type_name) - 1])
                ios.write("& ")
                ios.write("content")
                ios.write(",")
            elif body_schema:
                ios.write(" const " + operation_id + "Body& content,")        # response callback        
        ios.write(" std::function<void(int, const std::string&)> handler")


    def __parameters_vec_to_dict(self, params:list)->dict:
        rlt = {}
        for p in params :
            if p.get("$ref"):
                ref = p.get("$ref")
                if ref.startswith("#"):
                    obj = self.__get_object_from_path(ref)
                    rlt[obj.get("in") + "@" +obj.get("name")] = obj 
                else:
                    error("Invalid reference: parmeter reference should link to components/parameters")
            else:
                rlt[p.get("in") + "@" + p.get("name")] = p
        return rlt

    def __get_cpp_type_from_json_schema(self, schema:dict)->str:
        match schema.get("type"):
            case 'string':
                return 'const std::string&'
            case 'number':
                return 'float'
            case 'integer':
                fmt = schema.get("format")
                if fmt == 'int64':
                    return 'int64_t'
                return 'int'
            case 'boolean':
                return 'bool'
            case 'array':
                items = schema.get("items")
                return self.__get_cpp_const_type_for_array(items.get('type'))
            case 'object':
                if schema.get('title'):
                    return 'const ' + schema.get('title') + '&'
                else:
                    return 'const Poco::Dynamic::Struct&'
            case default:
                if schema.get('$ref'):
                    ref:str = schema.get('$ref')
                    return f'const {ref[(ref.rfind("/")+1):]}&'
                return default

    def __get_cpp_const_type_for_array(self, json_type:str)->str:
        match json_type:
            case 'string':
                return 'const std::vector<std::string>&'
            case 'number':
                return 'const std::vector<float>&'
            case 'integer':
                return 'const std::vector<int>&'
            case 'boolean':
                return 'const std::vector<bool>&'
            case default:
                return 'const std::vector<'+default+ '>&'

    def __get_cpp_type_for_array(self, json_type:str)->str:
        match json_type:
            case 'string':
                return 'std::vector<std::string>'
            case 'number':
                return 'std::vector<float>'
            case 'integer':
                return 'std::vector<int>'
            case 'boolean':
                return 'std::vector<bool>'
            case default:
                return 'std::vector<struct '+default+ '>'

    def __gen_schemas_declaration(self, schemas:list, header:TextIOWrapper)->None:
        header.write(self.__common_header_comment)
        header.write("#include \"xpack/json.h\"\n")

        ex_includes = []
        for schema in schemas:
            if schema.get('$ref'):
                self.__try_gen_header_from_single_schema(schema.get('$ref'), schema.get('x-file'))
                ex_includes.append("#include \"" + self.project + "/" + schema.get('x-name') + ".h\"\n")

        li = ex_includes       
        ex_includes = list(set(ex_includes))
        ex_includes.sort(key=li.index)

        for inc in ex_includes:
            header.write(inc)

        if self.namespace:
            header.write("namespace " + self.namespace + "\n")
            header.write("{\n")
        
        for schema in schemas:
            if not schema.get('$ref'):
                self.__write_schema(header, schema.get('x-name'), schema)

        if self.namespace:
                header.write("} //" + self.namespace +"\n")
            
    def __write_schema(self, header:TextIOWrapper, class_name:str, schema:dict)->None:
        if(schema.get("description")):
            header.write("  /**\n")
            header.write("  " + schema.get("description") + "\n")
            header.write("  */\n")

        data_type = schema.get("type")
        match data_type:
            case 'string':
                header.write("  typdef std::string " + class_name + ";\n")
            case 'number':
                header.write("  typedef float " + class_name + ";\n")
            case 'integer':
                header.write("  typedef int " + class_name + ";\n")
            case 'array':
                item_type = schema.get("items").get("type")
                item_ref = schema.get('items').get('$ref')
                if item_type:
                    header.write(f'  typedef {self.__get_cpp_type_for_array(item_type)} {class_name};\n' )
                elif item_ref:
                    header.write(f'  typedef {self.__get_cpp_type_for_array(item_ref[(item_ref.rfind("/")+1):])}  {class_name};\n')
            case 'object':
                header.write("  struct " + class_name +"\n")
                header.write("  {\n")
                properties:dict = schema.get("properties")
                for name, prop in properties.items():
                    match prop.get("type"):
                        case "string":
                            header.write("    std::string".ljust(35) + " " + name + ";\n")
                        case "number":
                            header.write("    float".ljust(35) +" " + name + ";\n")
                        case "integer":
                            if prop.get("format"):
                                match prop.get("format"):
                                    case "int32":
                                        header.write("    int32_t".ljust(35) +" " + name + ";\n")
                                    case "int64":
                                        header.write("    int64_t".ljust(35) +" " + name + ";\n")
                            else:
                                header.write("    int".ljust(35) +" " + name + ";\n")
                        case "boolean":
                            header.write("    bool".ljust(35) +" " + name + ";\n")
                        case "array":
                            item_type:str = prop.get("items").get("type")
                            ref = prop.get("items").get("$ref")
                            if ref:
                                    path:list = prop.get("items").get("$ref").split('/')
                                    item_type = path[len(path) - 1]
                                    item_type = item_type.removesuffix(".yaml")
                                    item_type = item_type.removesuffix('.json')
                            elif 'object' == item_type:
                                if prop.get("items").get("properties"):
                                    item_type = class_name + name.capitalize() + "Item"
                                else:
                                    error("should be a reference or special properties.")
                            header.write("    ")
                            header.write(self.__get_cpp_type_for_array(item_type).ljust(35) +" ")
                            header.write(name + ";\n")
                        case default:
                            if prop.get('$ref'):
                                path:list = prop.get("$ref").split('/')
                                type_name:str = path[len(path) - 1]
                                type_name = type_name.removesuffix(".yaml")
                                type_name = type_name.removesuffix('.json')
                                header.write("    struct " + type_name.ljust(35) +" " +  name + ";\n")
                            elif prop.get('properties'):
                                type_name = class_name + name.capitalize()
                                header.write("    struct " + type_name.ljust(35) +" " +  name + ";\n")
                            else:
                                Warning("should be a reference or special properties.")
                                header.write("    const std::string&".ljust(35)  +" " +  name + ";\n")
                header.write("\n")
                xpack_exp = "    XPACK("
                names:list = list(properties.keys())
                required:list = schema.get("required")
                if required:
                    xpack_exp += "M("
                    for item in required:
                        xpack_exp += item + ","
                    xpack_exp = xpack_exp[:-1]
                    xpack_exp += ")"
                    for name in names:
                        if name in required:
                            names.remove(name)
                if names:
                    if required:
                        xpack_exp += ", "
                    xpack_exp += "O("
                    for name in names :
                        xpack_exp += " " + name + ","
                    xpack_exp = xpack_exp[:-1]
                    xpack_exp += ")"
                xpack_exp += ");\n"
                header.write(xpack_exp)
                
                header.write("  };\n\n")

    def __gen_impl_header(self):
        self.__impl_header.write(self.__common_header_comment)
        self.__impl_header.write("#include \"" + self.project +"/core/ApiCore.h\"\n")
        self.__impl_header.write("#include \""+ self.project + "/" + self.__main_class_name +".h\"\n")
        self.__impl_header.write("\n")
        
        if self.namespace:
            self.__impl_header.write("namespace " + self.namespace + "\n")
            self.__impl_header.write("{\n")
        self.__impl_header.write("class " + self.__main_class_name + "Impl : public " + self.__main_class_name + "\n")
        self.__impl_header.write("{\n")
        self.__impl_header.write("public:\n")

        self.__impl_header.write("  " + self.__main_class_name + "Impl(std::shared_ptr<ApiCore> core);\n\n")
        self.__impl_header.write("  virtual void setServer(const std::string& server) override;\n\n")

        for path, item in self.__doc.get("paths").items():
            self.__impl_header.write("  // @group " + path + "\n\n")
            self.__write_methods_declaration(self.__impl_header, item, impl=True)
            self.__impl_header.write("\n")

        self.__impl_header.write("private:\n")
        self.__impl_header.write("  std::weak_ptr<ApiCore>  core_;\n")
        self.__impl_header.write("  std::string server_;\n")
                
        self.__impl_header.write("};\n")

    def __gen_impl_source_file(self):
        class_name = self.__main_class_name + "Impl"
        self.__impl_source.write("#include \"" + class_name + ".h\"\n" )
        self.__impl_source.write("#include <sstream>\n")
        self.__impl_source.write("#include <Poco/Net/HTTPRequest.h>\n")
        self.__impl_source.write("\n")
        if self.namespace:
            self.__impl_source.write("namespace " + self.namespace + "\n")
            self.__impl_source.write("{\n")

        self.__impl_source.write(class_name+"::" + class_name + "(std::shared_ptr<ApiCore> core)\n")
        self.__impl_source.write("  : core_(core)\n")
        self.__impl_source.write("{}\n\n")

        self.__impl_source.write("void " + class_name+"::"+"setServer(const std::string& server)\n")
        self.__impl_source.write("{\n")
        self.__impl_source.write("  server_ = server;\n")
        self.__impl_source.write("}\n\n")    
            
        for path, item in self.__doc.get("paths").items():
            self.__write_method_implemetation(self.__impl_source, path, item)

        self.__impl_source.write(f'{self.__main_class_name}* {self.project.upper()}_API create{self.__main_class_name}(std::shared_ptr<ApiCore> core)\n')
        self.__impl_source.write('{\n')
        self.__impl_source.write(f'  return new {class_name}(core);\n')
        self.__impl_source.write('}\n')

    def __write_method_implemetation(self, src:TextIOWrapper, path:str, item:dict):
        ref = item.get("$ref")
        if ref:
            if ref.startswith("#"):
                error("Invalid reference : " + ref)
            else:
                if ref.endswith(".yaml"):
                    stream = open(ref, "r", encoding="utf-8")
                    ref_item = yaml.load(stream, yaml.Loader)
                    self.__write_method_implemetation(src, path, ref_item)
                elif ref.endswith(".json"):
                    stream = open(ref, "r", encoding="utf-8")
                    ref_item = json.load(stream)
                    self.__write_method_implemetation(src, path, ref_item)
                else:
                    error("only support yaml or json reference.")    
        else:
            item_params = {}
            if item.get("parameters"):
                item_params = self.__parameters_vec_to_dict(item.get("parameters"))
            if item.get("get"):
                self.__write_operation_implementation(src, path, "Poco::Net::HTTPRequest::HTTP_GET", item.get("get"), item_params)
            if item.get("put"):
                self.__write_operation_implementation(src, path, "Poco::Net::HTTPRequest::HTTP_PUT", item.get("put"), item_params)
            if item.get("post"):
                self.__write_operation_implementation(src, path, "Poco::Net::HTTPRequest::HTTP_POST", item.get("post"), item_params)
            if item.get("delete"):
                self.__write_operation_implementation(src, path, "Poco::Net::HTTPRequest::HTTP_DELETE", item.get("delete"), item_params)
            if item.get("options"):
                self.__write_operation_implementation(src, path, "Poco::Net::HTTPRequest::HTTP_OPTIONS", item.get("options"), item_params)
            if item.get("head"):
                self.__write_operation_implementation(src, path, "Poco::Net::HTTPRequest::HTTP_HEAD", item.get("head"), item_params)
            if item.get("patch"):
                self.__write_operation_implementation(src, path, "Poco::Net::HTTPRequest::HTTP_PATCH", item.get("patch"), item_params)
            if item.get("trace"):
                self.__write_operation_implementation(src, path, "Poco::Net::HTTPRequest::HTTP_CONNECT", item.get("trace"), item_params)

    def __write_operation_implementation(self, src:TextIOWrapper, path:str, method:str, operation:dict, path_params:dict):
        params = path_params.copy()
        if operation.get("parameters"):
            operation_params:dict = self.__parameters_vec_to_dict(operation.get("parameters"))
            for n, p in operation_params.items():
                params[n] = p
                
        name_and_type= Path(self.document).name.split(".")
        class_name= name_and_type[0] + "Impl"
        src.write("int " + class_name + "::" + operation.get("operationId") + "(")
        self.__write_function_args(src, operation.get("operationId"), params, operation.get('requestBody'))
        src.write(")\n")
        src.write("{\n")

        src.write("  auto core = core_.lock();\n")
        src.write("  if (!core)\n")
        src.write("  {\n")
        src.write("    return -1;\n")
        src.write("  }\n\n")

        src.write("  ApiCore::Request req;\n")
        src.write("  req.type_ = "+ method + ";\n")
        src.write("  std::stringstream ss;\n")
        src.write('  ss<< server_')
        path = path.replace('{', '"<<').replace('}', '<<"')
        if path.startswith('"<<'):
            path = path.lstrip('"')
        else:
            path = '<<"' + path

        if path.endswith('<<"'):
            path = path.rstrip('<<"')
        else:
            path += '"'
        src.write(path + ";\n")

        has_query_param = False
        params = self.__merge_operation_parameters(path_params, operation)
        for param in params.values():
            if param.get('in') == 'query':
                schema = param.get('schema')
                if schema and ('object' == schema.get('type') or schema.get('$ref')):
                    ref = schema.get('$ref')
                    if ref:
                        param_obj = self.__get_object_from_path(ref)
                        if param_obj.get('type') == 'object':
                            properties = param_obj.get('properties')
                            for n, p in properties.items():
                                if not has_query_param:
                                    has_query_param = True
                                    src.write('  ss<<"?";\n')
                                else:
                                    src.write('  ss<<"&";\n')
                                src.write(f'  ss<< "{n}="<< {param.get("name")}.{n};\n')
                    else:
                        properties = schema.get('properties')
                        for n, p in properties.items():
                            if not has_query_param:
                                has_query_param = True
                                src.write('  ss<<"?";\n')
                            else:
                                src.write('  ss<<"&";\n')
                            src.write(f'  ss<< "{n}="<< {param.get("name")}.{n};\n')
                else:
                    if not has_query_param:
                        has_query_param = True
                        src.write('  ss<<"?";\n')
                    else:
                        src.write('  ss<<"&";\n')
                    src.write(f'  ss<< "{param.get("name")}="<< {param.get("name")};\n')
           
        src.write("  req.url_ = ss.str();\n")

        for param in params.values():
            if param.get('in') == 'header':
                src.write('  req.addtionHeaders_.insert("' + param.get('name') + '", '+param.get('name'))

        if operation.get('requestBody'):
            src.write("  req.body_ = xpack::json::encode(content);\n")
            src.write('  req.mimeType_ = "application/json";\n')

        src.write('  core->callMethod(req, handler);\n\n')
        src.write('  return 0;\n')

        src.write("}\n")
        src.write("\n")
        
    
    def __try_gen_header_from_single_schema(self, ref:str, path:str):
        if not ref or ((not ref.endswith('.yaml')) and (not ref.endswith('.json'))):
            return

        rs = ref.split('/')
        name = rs[len(rs)-1].removesuffix('.yaml').removesuffix('.json')

        file_path = self.output.joinpath('include', self.project, name + '.h')
        if file_path.exists():
            return
        
        s :dict = None
        if (len(path) == 0):
            ref_path = str(Path(self.document.removesuffix(Path(self.document).name)).joinpath(ref).absolute())
        else:
            ref_path = path
        
        stream = open(ref_path, "r", encoding="utf-8")
        if ref.endswith('.yaml'):
            s = yaml.load(stream, Loader=yaml.Loader)
        elif ref.endswith('.json'):
            s = json.load(stream)
        if not s:
            return

        schemas:list =[]
        self.__scan_schema(schema=s, ret_schemas=schemas, file=ref_path, name=name)

        schemas[0].setdefault('x-name', name)
        schemas[0]['x-name'] = name

        with open(file_path, 'w', encoding='utf-8') as header:
            self.__gen_schemas_declaration(schemas=schemas, header=header)
            
    def __gen_param_test_value(self, param:dict)->tuple:
        t = param.get('type')
        schema = param.get('schema')
        if schema:
            t = schema.get('type')
        
        faker = Faker(locale='en')
        match t:
            case 'string':
                return (faker.first_name(), True)
            case 'number':
                return (faker.unix_time(), False)
            case 'integer':
                return (faker.unix_time(), False)
            case 'boolean':
                return ('true', False)
            # case 'array':
            # case 'object':
            case _:
                return ('None', True)
    def __get_body_classname(self, operationId:str, body:dict)->str:
        content = body.get('content')
        if content:
            app = content.get('application/json')
            if not app:
                app = content.get("'*/*'")
            if app:
                schema = app.get('schema')
                if schema:
                    ref = schema.get('$ref')
                    if ref:
                        return ref[ref.rfind('/')+1:]
        return operationId + 'Body'
            
    def __gen_operation_test_case(self, path:str, method:str, operation:dict, path_params:dict)->str:
        code =''
        code += f'TEST_F({self.__main_class_name}Test, {operation.get("operationId")})\n'
        code += '{\n'
        code += '  TestRequest req;\n'
        code += f'  req.method={method};\n'
        
        final_path = path
        params = self.__merge_operation_parameters(path_params, operation)
        has_query_param = False
        args = []
        for param in params.values():
            val = self.__gen_param_test_value(param)
            args.append(val)
            if param.get('in') == 'path':
                final_path = final_path.replace("{" + param.get('name') + "}", str(val[0]))
            elif param.get('in') == 'query':
                if not has_query_param:
                    has_query_param = True
                    final_path += '?'
                else:
                    final_path += '&'
                final_path += f'{param.get("name")}={val[0]}'
        code += f'  req.path="{final_path}";\n'

        body = operation.get('requestBody')
        if body:
            code += f'  {self.__get_body_classname(operation.get("operationId"), body)} body;\n'
            code += '  req.content = xpack::json::encode(body);\n'
        code += f'\n  _agent->{operation.get("operationId")}('
        for arg in args:
            if arg[1]:
                code += f'"{arg[0]}",'
            else:
                code += f'{arg[0]},'
        if body:        
            code += 'body, '
        code += '[req](int code, const std::string&reason, const std::string& rsp){\n'
        code += '    EXPECT_EQ(code, 200);\n'
        code += '    TestRequest r;\n'
        code += '    xpack::json::decode(rsp, r);\n'
        code += '    EXPECT_EQ(r, req);\n'
        code += '  });\n\n'
        
        code += '}\n'
        return code
            
    def __gen_path_test_case(self, path:str, item:dict) ->str:
        ref = item.get("$ref")
        if ref:
            if ref.startswith("#"):
                error("Invalid reference : " + ref)
            else:
                if ref.endswith(".yaml"):
                    stream = open(ref, "r", encoding="utf-8")
                    ref_item = yaml.load(stream, yaml.Loader)
                    return self.__gen_path_test_case(path, ref_item)
                elif ref.endswith(".json"):
                    stream = open(ref, "r", encoding="utf-8")
                    ref_item = json.load(stream)
                    return self.__gen_path_test_case(path, ref_item)
                else:
                    error("only support yaml or json reference.")    
        else:
            item_params = {}
            if item.get("parameters"):
                item_params = self.__parameters_vec_to_dict(item.get("parameters"))
            if item.get("get"):
                return self.__gen_operation_test_case(path, "Poco::Net::HTTPRequest::HTTP_GET", item.get("get"), item_params)
            if item.get("put"):
                return self.__gen_operation_test_case(path, "Poco::Net::HTTPRequest::HTTP_PUT", item.get("put"), item_params)
            if item.get("post"):
                return self.__gen_operation_test_case(path, "Poco::Net::HTTPRequest::HTTP_POST", item.get("post"), item_params)
            if item.get("delete"):
                return self.__gen_operation_test_case(path, "Poco::Net::HTTPRequest::HTTP_DELETE", item.get("delete"), item_params)
            if item.get("options"):
                return self.__gen_operation_test_case(path, "Poco::Net::HTTPRequest::HTTP_OPTIONS", item.get("options"), item_params)
            if item.get("head"):
                return self.__gen_operation_test_case(path, "Poco::Net::HTTPRequest::HTTP_HEAD", item.get("head"), item_params)
            if item.get("patch"):
                return self.__gen_operation_test_case(path, "Poco::Net::HTTPRequest::HTTP_PATCH", item.get("patch"), item_params)
            if item.get("trace"):
                return self.__gen_operation_test_case(path, "Poco::Net::HTTPRequest::HTTP_CONNECT", item.get("trace"), item_params)

    def __gen_paths_test_case(self)->str:
        code :str = ''
        for path, item in self.__doc.get("paths").items():
            code += self.__gen_path_test_case(path, item)
            code += '\n'
        return code

    def __gen_test_source(self):
        self.output.joinpath('test').mkdir(parents=True, exist_ok=True)
        test_src = str(self.output.joinpath('test', f'{self.__main_class_name}Test.cxx'))
        shutil.copy(os.path.join(os.path.dirname(__file__), 'tmpl', 'test.cxx'), test_src)

        self.__replace_in_file(test_src, '@NAMESPACE@', self.namespace)
        self.__replace_in_file(test_src, '@PROJECT@', self.project)
        self.__replace_in_file(test_src, '@TEST_CLASS@', f'{self.__main_class_name}Test')
        self.__replace_in_file(test_src, '@CLASS@', self.__main_class_name)
        self.__replace_in_file(test_src, '@TEST_CASES@', self.__gen_paths_test_case())    

    def __replace_in_file(self, path:str, ori:str, replace:str):
        with fileinput.FileInput(path, inplace=True, backup='.bak') as file:
            for line in file:
                print(line.replace(ori, replace), end='')
        os.remove(path+'.bak')
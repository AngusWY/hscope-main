#!/usr/bin/env python3

from engine.config.constants import ENGINE_INTERNAL
from engine.util import util

common_type_table0 = {
    "auto"                          : "",
    "any"                           : "",
    "object"                        : "",

    "NoneType"                      : ENGINE_INTERNAL.NULL,
    "bool"                          : ENGINE_INTERNAL.BOOL,
    "boolean"                       : ENGINE_INTERNAL.BOOL,
    "char"                          : ENGINE_INTERNAL.I8,
    "signed char"                   : ENGINE_INTERNAL.I8,
    "unsigned char"                 : ENGINE_INTERNAL.U8,
    "short"                         : ENGINE_INTERNAL.I16,
    "signed short"                  : ENGINE_INTERNAL.I16,
    "unsigned short"                : ENGINE_INTERNAL.U16,
    "signed int"                    : ENGINE_INTERNAL.I32,
    "unsigned int"                  : ENGINE_INTERNAL.U32,
    "signed long"                   : ENGINE_INTERNAL.I64,
    "unsigned long"                 : ENGINE_INTERNAL.U64,
    "long long"                     : ENGINE_INTERNAL.I64,
    "unsigned long long"            : ENGINE_INTERNAL.U64,
    "float"                         : ENGINE_INTERNAL.F32,
    "double"                        : ENGINE_INTERNAL.F64,
    "long double"                   : ENGINE_INTERNAL.F64,
    "wchar_t"                       : ENGINE_INTERNAL.I16,
    "char16_t"                      : ENGINE_INTERNAL.I16,
    "char32_t"                      : ENGINE_INTERNAL.I32,
    "int8_t"                        : ENGINE_INTERNAL.I8,
    "int16_t"                       : ENGINE_INTERNAL.I16,
    "int32_t"                       : ENGINE_INTERNAL.I32,
    "int_t"                         : ENGINE_INTERNAL.I32,
    "int64_t"                       : ENGINE_INTERNAL.I64,
    "uint8_t"                       : ENGINE_INTERNAL.U8,
    "uint16_t"                      : ENGINE_INTERNAL.U16,
    "uint32_t"                      : ENGINE_INTERNAL.U32,
    "uint64_t"                      : ENGINE_INTERNAL.U16,
    "size_t"                        : ENGINE_INTERNAL.I64,
    "ssize_t"                       : ENGINE_INTERNAL.I64,
    "isize"                         : ENGINE_INTERNAL.POINTER,

    "uintptr_t"                     : ENGINE_INTERNAL.POINTER,
    "nullptr_t"                     : ENGINE_INTERNAL.POINTER,
    "ptr_t"                         : ENGINE_INTERNAL.POINTER,
    "ptr"                           : ENGINE_INTERNAL.POINTER,
    "uintptr"                       : ENGINE_INTERNAL.POINTER,

    "string"                        : ENGINE_INTERNAL.STRING,
    "String"                        : ENGINE_INTERNAL.STRING,
    "str"                           : ENGINE_INTERNAL.STRING,

    "vector"                        : ENGINE_INTERNAL.ARRAY,
    "Vector"                        : ENGINE_INTERNAL.ARRAY,
    "list"                          : ENGINE_INTERNAL.ARRAY,
    "List"                          : ENGINE_INTERNAL.ARRAY,

    "dict"                          : ENGINE_INTERNAL.RECORD,
}

common_type_table_for_typed_language = {
    **common_type_table0,
    "int"                           : ENGINE_INTERNAL.I32,
    "float"                         : ENGINE_INTERNAL.F32,
}

common_type_table_for_untyped_language = {
    **common_type_table0,
    "int"                           : ENGINE_INTERNAL.INT,
    "float"                         : ENGINE_INTERNAL.FLOAT,
}

lang_type_table = {
    "c": common_type_table_for_typed_language,
    "java": common_type_table_for_typed_language,
    "llvm": common_type_table_for_typed_language,
    "mir": common_type_table_for_typed_language,
    "python": common_type_table_for_untyped_language,
    "javascript": common_type_table_for_untyped_language,
    "php": common_type_table_for_untyped_language,
}

built_data_types = set()
for table in [common_type_table0, common_type_table_for_typed_language, common_type_table_for_untyped_language]:
    for value in table.values():
        if value:
            built_data_types.add(value)

def get_lang_type_table(lang):
    return lang_type_table.get(lang, common_type_table0)

def determine_constant_type(name):
    result = None

    if util.isna(name):
        return result

    if name == ENGINE_INTERNAL.NULL:
        result = ENGINE_INTERNAL.NULL

    elif name in [ENGINE_INTERNAL.TRUE, ENGINE_INTERNAL.FALSE]:
        result = ENGINE_INTERNAL.BOOL

    elif "'" in name or '"' in name:
        result = ENGINE_INTERNAL.STRING

    else:
        try:
            int(name)
            result = ENGINE_INTERNAL.INT
        except ValueError:
            pass

        if result is None:
            try:
                float(name)
                result = ENGINE_INTERNAL.FLOAT
            except ValueError:
                pass

        if result is None:
            result = ENGINE_INTERNAL.STRING

    return result

def is_builtin_type(data_type):
    return data_type in built_data_types

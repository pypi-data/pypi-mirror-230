import keyword
import os
import re


def convert_name_to_python(name):
    if not name:
        return name

    # special case :)
    name = name.replace("@v", "_version")
    if name == "id":
        name = name.replace("id", "_id")
    # Replace any spaces or special characters in the string with an underscore
    identifier = re.sub(r"[^\w\s]", "_", name)
    identifier = re.sub(r"\s+", "_", identifier)

    # Ensure that the first character of the identifier is a letter or an underscore
    if identifier[0].isdigit():
        identifier = "_" + identifier

    # Ensure that the resulting identifier is not a reserved keyword in Python
    if keyword.iskeyword(identifier):
        identifier = identifier + "_"

    return identifier


def capitalize(s):
    return s[0].capitalize() + s[1:]


def convert_name_to_python_class(name):
    class_name = "".join([capitalize(word) for word in name.split("-")])
    class_name = "".join([capitalize(word) for word in class_name.split("_")])

    # Replace any spaces or special characters in the string with an underscore
    class_name = re.sub(r"[^\w\s]", "", class_name)
    class_name = re.sub(r"\s+", "_", class_name)

    if class_name[0].isdigit():
        class_name = "_" + class_name

    return class_name


def package_name(value):
    if not value:
        return None
    return value.rsplit(".", maxsplit=1)[0]


def split_package_name(value):
    return package_name(value)


def base_name(value):
    if not value:
        return None
    return value.rsplit(".", maxsplit=1)[-1]


def split_base_name(value):
    return base_name(value)


def split_package_base_name(value):
    if "." not in value:
        return None, value
    return value.rsplit(".", maxsplit=1)


def qualified_name(package_name: str, class_name: str):
    if "." not in class_name:
        return f"{package_name}.{class_name}"
    if class_name.startswith("."):
        # package_name: aaa.bbb, class name .C => aaa.bbb.C
        # package_name: aaa.bbb, class name ..C => aaa.C
        # package_name: aaa.bbb, class name ...C => C
        class_name = class_name[1:]
        package_path = package_name.split(".")
        while class_name.startswith("."):
            if package_path:
                package_path = package_path[:-1]
            class_name = class_name[1:]
        if package_path:
            class_name = f"{'.'.join(package_path)}.{class_name}"
    return class_name


def convert_config_to_qualified_name(
    config_section, module_field="module", name_field="class"
):
    module = config_section[module_field]
    class_name = config_section[name_field]
    qualified = qualified_name(module, class_name)
    if qualified != class_name:
        config_section[name_field] = qualified


def module_to_path(module):
    return os.path.join(*module.split("."))


def parent_module(module):
    return ".".join(module.split(".")[:-1])

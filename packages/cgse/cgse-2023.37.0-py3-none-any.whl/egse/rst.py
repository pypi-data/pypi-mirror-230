import yaml
import logging
import inspect
import textwrap

module_logger = logging.getLogger(__name__)


def create_args_list(cmd):
    s = ""
    if 'args' not in cmd:
        return s
    for arg_name in cmd['args'].keys():
        s += f"{arg_name}, "
    if 'kwargs' not in cmd:
        return s[:-2]
    for arg_name in cmd['kwargs'].keys():
        s += f"{arg_name}={cmd['kwargs'][arg_name].split('|')[1].strip()}, "
    return s[:-2]


def handle_description(d):
    s = textwrap.indent(inspect.cleandoc(d), "      ")
    return s + "\n\n"


def handle_args(d):
    s = ""
    for arg_name in d:
        arg_type, arg_desc = [x.strip() for x in d[arg_name].split('|', 1)]
        s += f"      :param {arg_type} {arg_name}: {arg_desc}\n"
    return s + "\n\n"


def handle_kwargs(d):
    s = ""
    for arg_name in d:
        arg_type, arg_default, arg_desc = [x.strip() for x in d[arg_name].split('|', 2)]
        s += f"      :param {arg_type} {arg_name}: {arg_desc} [default: {arg_default}]"
    return s + "\n\n"


def handle_returns(d):
    s = ""
    if d == "None":
        return s
    return_type, return_desc = [x.strip() for x in d.split('|', 2)]
    s += f"      :returns: (*{return_type}*) {return_desc}\n"
    # s += f"      :rtype: {return_type}\n"
    return s + "\n"


def handle_todos(d):
    return f"      .. todo:: {d}\n\n"


def handle_notes(d):
    return f"      .. note:: {d}\n\n"


def handle_class_description(d):
    s = textwrap.indent(inspect.cleandoc(d), "   ")
    return s + "\n\n"


class RSTError(Exception):
    pass


class ReStructuredText(object):
    """
    .. todo:: implement proper indentation though a instance variable or something
    .. todo:: there should also be overall class documentation loaded from the YAML file
    """

    def __init__(self):
        pass

    def _read_yaml(self, filename):
        with open(filename, 'r') as stream:
            try:
                yaml_document = yaml.load(stream)
            except yaml.YAMLError as exc:
                module_logger.error(exc)
                raise RSTError(f"Error loading YAML document {filename}") from exc
        return yaml_document

    def create_auto_class_from_yaml(self, yaml_file):

        yaml_document = self._read_yaml(yaml_file)

        class_name = yaml_document['ProxyClass']

        rst_msg = f".. class:: {class_name}\n\n"

        if 'ClassDescription' in yaml_document:
            rst_msg += handle_class_description(yaml_document['ClassDescription'])

        cmd_tag = "Commands"

        for cmd in yaml_document[cmd_tag]:
            rst_msg += self.create_command(yaml_document[cmd_tag], cmd)
            rst_msg += "\n"

        return rst_msg

    def create_command(self, d, cmd):

        rst_msg = f"   .. method:: {cmd}({create_args_list(d[cmd])})\n\n"

        d = d[cmd]

        if 'description' in d:
            rst_msg += handle_description(d['description'])

        if 'args' in d:
            rst_msg += handle_args(d['args'])

        if 'kwargs' in d:
            rst_msg += handle_kwargs(d['kwargs'])

        if 'returns' in d:
            rst_msg += handle_returns(d['returns'])

        if 'todo' in d:
            rst_msg += handle_todos(d['todo'])

        if 'note' in d:
            rst_msg += handle_notes(d['note'])

        return rst_msg


if __name__ == "__main__":
    pass

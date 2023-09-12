import os.path as op
import os
import shutil
from jinja2 import Environment, FileSystemLoader, Undefined
import git

from genesia.clean_and_format_code import clean_and_format_code
# from genesia.run_django_server import run_django_server

available_templates_url = {
    "django": "https://github.com/genesia-dev/django-template.git",
    "react": "https://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@github.com/lucasmrdt/chatcoder-react-template.git",
}

available_templates = available_templates_url.keys()


class SilentUndefined(Undefined):
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.name = name

    def _fail_with_undefined_error(self, *args, **kwargs):
        name = self.name

        class EmptyString(str):
            def __call__(self, *args, **kwargs):
                return f"{{{{name}}}}"

        return EmptyString()

    __add__ = (
        __radd__
    ) = (
        __mul__
    ) = (
        __rmul__
    ) = (
        __div__
    ) = (
        __rdiv__
    ) = (
        __truediv__
    ) = (
        __rtruediv__
    ) = (
        __floordiv__
    ) = (
        __rfloordiv__
    ) = (
        __mod__
    ) = (
        __rmod__
    ) = (
        __pos__
    ) = (
        __neg__
    ) = (
        __call__
    ) = (
        __getitem__
    ) = (
        __lt__
    ) = (
        __le__
    ) = (
        __gt__
    ) = (
        __ge__
    ) = (
        __int__
    ) = __float__ = __complex__ = __pow__ = __rpow__ = _fail_with_undefined_error


def fill_jinja_templates(template_path: str, data: dict, output_path: str) -> None:
    # Iterate through all files and subdirectories
    for root, _, files in os.walk(template_path):
        for file_name in files:
            if file_name.endswith(".jinja"):
                full_path = os.path.join(root, file_name)
                filled_template = fill_jinja_template(full_path, data)

                # Create the corresponding output directory and file
                relative_path = os.path.relpath(root, template_path)
                output_dir = os.path.join(output_path, relative_path)
                os.makedirs(output_dir, exist_ok=True)
                output_file_path = os.path.join(
                    output_dir, file_name.replace(".jinja", "")
                )

                with open(output_file_path, "w") as output_file:
                    output_file.write(filled_template)


def fill_jinja_template(template_path: str, data: dict) -> str:
    # Get the path and filename separately
    base_dir = os.path.dirname(template_path)
    template_name = os.path.basename(template_path)

    # Create a Jinja2 environment and load the template
    env = Environment(loader=FileSystemLoader(
        base_dir), undefined=SilentUndefined)
    env.filters["pascal_case"] = pascal_case

    # TEMPORARY, ALLOW TO CREATE A NEW FIELD AS A PROCESSED VALUE OF ANOTHER FIELD
    import re

    def extract_path_parameters(url_pattern: str):
        matches = re.findall(r'<int:(\w+)>', url_pattern)
        return ', '.join(matches)

    env.filters['extract_path_parameters'] = extract_path_parameters
    # END TEMPORARY

    env.trim_blocks = True
    env.lstrip_blocks = True
    template = env.get_template(template_name)

    # Fill the template with the provided data
    filled_template = template.render(data)

    return filled_template


def pascal_case(s):
    parts = s.split("_")
    return "".join(part.capitalize() for part in parts)


def create_project_from_template(template_name, project_name, jinja_result):
    assert template_name in available_templates, f"Unknown template {template_name}"
    assert not op.exists(project_name), f"Project {project_name} already exists"

    template_dir = "genesia-templates"

    git.Repo.clone_from(available_templates_url[template_name], template_dir)

    # copy directory
    shutil.copytree(template_dir, project_name)
    # change folder name that are named {{project_name}} to the actual project name
    for root, dirs, files in os.walk(project_name):
        for dir in dirs:
            if "{{project_name}}" in dir:
                shutil.move(
                    op.join(root, dir),
                    op.join(root, dir.replace(
                        "{{project_name}}", project_name)),
                )
    jinja_result["project_name"] = project_name
    jinja_result["app_name"] = "app"

    # fill jinja templates
    fill_jinja_templates(project_name, jinja_result, project_name)
    # remove jinja templates
    for root, dirs, files in os.walk(project_name):
        for file in files:
            if file.endswith(".jinja"):
                os.remove(op.join(root, file))

    shutil.rmtree(template_dir)

    clean_and_format_code(project_name)
    # run_django_server(project_name)

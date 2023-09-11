#!/usr/bin/env python3

import shlex
import subprocess
import os
from util import Term, resource_content
from cli import create_cli


DEV_DEPENDENCIES = 'pytailwindcss websockets python-dotenv'


LIVE_RELOAD_SCRIPT = resource_content('live_reload.js')
DEV_SCRIPT = resource_content('dev.py')
TAILWIND_CONFIG = resource_content('tailwind.config.js')
LAYOUT_TEMPLATE = resource_content('layout.html')


def generate_tw_config(content_glob: str) -> str:
    return TAILWIND_CONFIG.content.replace(
        '{content_glob_placeholder}',
        content_glob
    )


def generate_dev_script(css_file: str, minified_css_file: str) -> str:
    return DEV_SCRIPT.content \
        .replace(
            '{tailwindcss_output_placeholder}',
            css_file
        ).replace(
            '{tailwindcss_minified_output_placeholder}',
            minified_css_file
        )


def generate_live_reload_template(css_file: str, js_file: str, minified_css_file: str) -> str:
    return ('''
  {% if config.DEBUG %}
    <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename=\'''' + css_file + '''\') }}">
    <script src="{{ url_for('static', filename=\'''' + js_file + '''\') }}" defer></script>
  {% else %}
    <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename=\'''' + minified_css_file + '''\') }}">
  {% endif %}
''').strip()


def generate_layout_template(css_file: str, js_file: str, minified_css_file: str) -> str:
    return LAYOUT_TEMPLATE.content.replace(
        '{live_reload_template_placeholder}',
        generate_live_reload_template(css_file, js_file, minified_css_file)
    )


def check_installation_requirements() -> int:
    cwd = os.getcwd()
    print(
        f'The modding will continue on the current working directory:\n> {Term.BOLD}{cwd}{Term.END} ')
    continue_install = Term.confirm("Continue?")

    if not continue_install:
        Term.dev("modding canceled")
        return 1

    python_cmd = shlex.split("python --version")
    python_cmd_result = subprocess.run(
        python_cmd, shell=True, check=True, capture_output=True
    )

    if python_cmd_result.returncode != 0:
        Term.error('python --version failed, terminating script')
        return python_cmd_result.returncode

    version = python_cmd_result.stdout.decode('utf-8')
    if version != 'Python 3.8.10':
        Term.warn("Current python version is 3.8.10")
        continue_install = Term.confirm("Continue?")
        if not continue_install:
            Term.dev("modding canceled")
            return 1

    return 0


def install_dev_dependencies() -> None:
    Term.dev('Installing required dev dependencies...')

    poetry_cmd = shlex.split(f"poetry add --group=dev {DEV_DEPENDENCIES}")

    try:
        result = subprocess.run(poetry_cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        Term.error(e)
        Term.info('Dev dependencies installation failed, terminating script')
        exit(1)

    if result.returncode != 0:
        Term.info('Dev dependencies installation failed, terminating script')
        exit(result.returncode)

    Term.dev('Dev dependencies installation complete')


def init_tailwindcss(content_glob: str) -> None:
    Term.dev('Initializing tailwindcss...')

    tailwind_init = "tailwindcss init"

    try:
        result = subprocess.run(tailwind_init, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        Term.error(e)
        Term.info('Tailwindcss initialization failed, terminating script')
        exit(1)

    if result.returncode != 0:
        Term.info('Tailwindcss initialization failed, terminating script')
        exit(result.returncode)

    with open('tailwind.config.js', 'w') as f:
        f.write(generate_tw_config(content_glob))

    Term.dev('Tailwindcss initialization complete')


def generate_files(live_reload_file: str, twcss_file: str, minified_twcss_file: str) -> None:
    with open(DEV_SCRIPT.name, 'w') as f:
        f.write(generate_dev_script(twcss_file, minified_twcss_file))

    try:
        with open(live_reload_file, 'w') as f:
            f.write(LIVE_RELOAD_SCRIPT.content)

    except FileNotFoundError:
        os.makedirs(
            os.path.dirname(live_reload_file),
            exist_ok=True
        )
        with open(live_reload_file, 'w') as f:
            f.write(LIVE_RELOAD_SCRIPT.content)


def update_layout(templates_dir: str, root_layout_template: str, static_dir: str, live_reload_file: str, twcss_file: str, minified_twcss_file: str) -> None:
    root_layout = f'{templates_dir}/{root_layout_template}'

    try:
        with open(root_layout, '+r') as f:
            layout = f.read()
            if '</head>' not in layout:
                print("Error: </head> tag not found in src/web/templates/layout.html")
                exit(1)
            layout = layout.replace(
                '</head>',
                generate_live_reload_template(
                    twcss_file,
                    live_reload_file,
                    minified_twcss_file
                ) + '</head>'
            )
            f.seek(0)
            f.write(layout)
            f.truncate()
    except FileNotFoundError as e:
        Term.warn(e)
        os.makedirs(
            os.path.dirname(root_layout),
            exist_ok=True
        )
        with open(root_layout, 'w') as f:
            f.write(generate_layout_template(
                twcss_file,
                live_reload_file,
                minified_twcss_file
            ))


def update_gitignore(static_dir: str, twcss_file: str) -> None:
    content = f'''
# flask-live-twcss
{static_dir}/{twcss_file}
'''

    try:
        with open('.gitignore', 'a') as f:
            f.write(content)
    except FileNotFoundError:
        Term.info('Missing .gitignore file, creating one...')
        with open('.gitignore', 'w') as f:
            f.write(content)


def main() -> None:
    cli_args = create_cli().parse_args()

    Term.dev('Starting modding...')

    check_code = check_installation_requirements()
    if check_code != 0:
        exit(check_code)

    install_dev_dependencies()

    content_glob = f'{cli_args.templates_folder}/{cli_args.templates_glob}'
    init_tailwindcss(content_glob)

    generate_files(
        cli_args.live_reload_file,
        cli_args.generated_css_file,
        cli_args.minified_css_file
    )

    update_layout(
        cli_args.templates_folder,
        cli_args.template_root_layout,
        cli_args.static_folder,
        cli_args.live_reload_file,
        cli_args.generated_css_file,
        cli_args.minified_css_file
    )

    if cli_args.gitignore:
        update_gitignore(
            cli_args.live_reload_file,
            cli_args.generated_css_file
        )

    Term.dev(f'Modding complete ✅')
    exit(0)


if __name__ == "__main__":
    main()

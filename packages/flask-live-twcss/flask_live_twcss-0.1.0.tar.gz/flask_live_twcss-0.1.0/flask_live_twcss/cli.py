import argparse


DEFAULT_STATIC_FOLDER = 'static'

DEFAULT_TEMPLATE_FOLDER = 'templates'
DEFAULT_TEMPLATE_GLOB = '**/*.html'
DEFAULT_TEMPLATE_ROOT_LAYOUT = 'layout.html'

DEFAULT_LIVE_RELOAD_FILE = 'dev/live_reload.js'

DEFAULT_TWCSS_FILE = 'dev/tailwindcss.css'

DEFAULT_MINIFIED_TWCSS_FILE = 'tailwindcss_min.css'

DEFAULT_UPDATE_GITIGNORE = False


def create_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Mods a Flask app to use TailwindCSS in a dev server like manner.',
        allow_abbrev=True
    )

    parser.add_argument(
        '-gi', '--gitignore', dest='gitignore', action='store_true', default=DEFAULT_UPDATE_GITIGNORE,
        help=f'Update .gitignore to exclude dev mode related files. Default: {DEFAULT_UPDATE_GITIGNORE}'
    )

    parser.add_argument(
        '-s', '--static-folder', dest='static_folder', type=str, default=DEFAULT_STATIC_FOLDER,
        help=f'Static folder path. Default: {DEFAULT_STATIC_FOLDER}'
    )

    parser.add_argument(
        '-tf', '--templates-folder', dest='templates_folder', type=str, default=DEFAULT_TEMPLATE_FOLDER,
        help=f'Templates folder path. Default: {DEFAULT_TEMPLATE_FOLDER}'
    )
    parser.add_argument(
        '-tg', '--templates-glob', dest='templates_glob', type=str, default=DEFAULT_TEMPLATE_GLOB,
        help=f'Templates glob pattern. Default: {DEFAULT_TEMPLATE_GLOB}'
    )
    parser.add_argument(
        '-trl', '--template-root-layout', dest='template_root_layout', type=str, default=DEFAULT_TEMPLATE_ROOT_LAYOUT,
        help=f'Template root layout file. Default: {DEFAULT_TEMPLATE_ROOT_LAYOUT}'
    )

    parser.add_argument(
        '-lrjs', '--live-reload-file', dest='live_reload_file', type=str, default=DEFAULT_LIVE_RELOAD_FILE,
        help=f'Live reload js file, relative to static folder. Default: {DEFAULT_LIVE_RELOAD_FILE}'
    )
    parser.add_argument(
        '-gcf', '--generated-css-file', dest='generated_css_file', type=str, default=DEFAULT_TWCSS_FILE,
        help=f'Generated css file, relative to static folder. Default: {DEFAULT_TWCSS_FILE}'
    )
    parser.add_argument(
        '-mcf', '--minified-css-file', dest='minified_css_file', type=str, default=DEFAULT_MINIFIED_TWCSS_FILE,
        help=f'Minified css file, relative to static folder. Default: {DEFAULT_MINIFIED_TWCSS_FILE}'
    )

    return parser

import os.path


# https://www.sphinx-doc.org/en/master/development/theming.html#distribute-your-theme-as-a-python-package
def setup(app):
    app.add_html_theme(
        __package__, os.path.abspath(os.path.dirname(__file__)))

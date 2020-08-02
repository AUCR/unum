"""AUCR Unum Unified File Upload System plugin framework."""
# coding=utf-8
from aucr_app.plugins.unum.routes import unum
from aucr_app.plugins.unum.api.file import api_page as unum_api_page


def load(app):
    """Load overrides for Unum plugin to work properly."""
    app.register_blueprint(unum, url_prefix='/unum')
    app.register_blueprint(unum_api_page, url_prefix='/api')


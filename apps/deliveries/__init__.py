# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import Blueprint

blueprint = Blueprint(
    'deliveries_blueprint',
    __name__,
    url_prefix='/deliveries',
    template_folder='templates',
    static_folder='static'
)

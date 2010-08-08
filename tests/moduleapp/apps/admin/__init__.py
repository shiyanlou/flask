import os
from flask import Module, render_template


admin = Module(__name__, url_prefix='/admin', static_path='static')


@admin.route('/')
def index():
    return render_template('admin/index.html')

from flask import Flask


app = Flask(__name__)
from modulecompat.test import mod
app.register_module(mod, url_prefix='/test')

"""DEMO: deliberately broken agent fix to exercise the CI gate."""
from flask import Flask, _this_does_not_exist  # boot will fail

app = Flask(__name__)

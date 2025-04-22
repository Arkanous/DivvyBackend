from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import sqlite3
import os


# Init app
app = Flask(__name__)

# Example Http Request
@app.route('/', methods=['GET'])
def home():
    return "TEST"
import dash
import flask
import dash_bootstrap_components as dbc

# bootstrap theme
# https://bootswatch.com/lux/
external_stylesheets = [dbc.themes.LUX]

flask_server = flask.Flask(__name__)
app = dash.Dash(__name__, server=flask_server, external_stylesheets=external_stylesheets)
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# server = app.server
app.config.suppress_callback_exceptions = True
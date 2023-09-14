"""Allow an API Wrapper for the CLI"""
import os
import base64
from typing import Union
from os import getenv
import subprocess
from wsgiref import simple_server

import pandas as pd
from rich.console import Console
from click import Group, Command
from flask import Flask, render_template_string, request, redirect, url_for
from flask import render_template, Response
from flask_rebar import Rebar
from flask_restx import Api
from werkzeug.utils import secure_filename

from regscale import __version__
from regscale.core.server.helpers import (
    create_view_func,
    generate_parameters_model,
    get_site_info,
    get_catgalogues,
)
from regscale.regscale import cli
from regscale.core.app.public.fedramp.import_fedramp_r4_ssp import (
    parse_and_load_xml_rev4,
)
from regscale.core.app.logz import create_logger
from regscale.core.app.internal.login import login
from regscale.core.app.utils.regscale_utils import update_regscale_config

# pylint: disable=line-too-long, logging-fstring-interpolation, invalid-name

current_file_size = 0

app = Flask(__name__)


logger = create_logger()


@app.route("/")
def index():
    """Index route"""
    return redirect(url_for("home"))


# setup swagger
api = Api(
    app,
    version=__version__,
    title="RegScale-CLI REST API Wrapper",
    description="A REST API wrapper support GET and POST requests for the RegScale-CLI.",
    doc="/swagger/",
    default="RegScale-CLI REST API",
    default_label="RegScale-CLI REST API Operations",
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    debug=True,
)
# setup redoc
rebar = Rebar()
registry = rebar.create_handler_registry()

if not os.path.exists("artifacts"):
    os.makedirs("artifacts")


# recursive function to generate routes from a click group
def generate_routes(api_instance: Api, group: Union[Group, Command], path: str = ""):
    """Generate routes for the app, recursively
    since group is assumed to be a click.Group, we get the command_name and command for all of those items.
    an endpoint_path is created. if the command is found to be a click.Group it is called on itself until we have a
    click command.
    :param Api api_instance: the flask_restx.Api instance
    :param group: A Group or Command from click
    :param path: str a representation of the endpoint path
    """
    for command_name, command in group.commands.items():
        endpoint_path = f"{path}/{command_name}"
        if command.name in {
            "encrypt",
            "decrypt",
            "change_passkey",
            "catalog",
            "assessments",
            "control_editor",
        }:
            continue
        if isinstance(command, Group) and command.name in {"issues"}:
            continue
        if isinstance(command, Group):
            # Generate routes for nested group
            generate_routes(api_instance, command, endpoint_path)
        else:
            # generate the CommandResource class
            resource_class = create_view_func(command)
            # if command has params, generate the parameters model for that command
            if command.params:
                # generate the parameters model
                parameters_model = generate_parameters_model(api_instance, command)
                resource_class.post = api.expect(parameters_model)(resource_class.post)
            api.add_resource(resource_class, endpoint_path)


# generate all the routes dynamically from the click information
generate_routes(api, cli)


@app.route("/redoc/")
def redoc():
    """return render template string"""
    return render_template_string(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>ReDoc</title>
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
            <style>
                body, html { margin: 0; padding: 0; }
                #redoc { width: 100vw; height: 100vw; position: sticky; }
            </style>
        </head>
        <body>
            <div id="redoc"></div>
            <script src="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"> </script>
            <script>
                Redoc.init('/swagger.json', {}, document.getElementById('redoc'))
            </script>
        </body>
        </html>
    """
    )


@app.route("/home")
def home():
    """Index route"""
    return render_template("index.html", site_info=get_site_info())


@app.route("/auth", methods=["GET"])
def auth():
    """Auth route"""
    return render_template("login.html", site_info=get_site_info())


@app.route("/login-token", methods=["POST"])
def login_token():
    domain = request.form["domain"].split(" ")[0]  # split on space to avoid injection
    token = request.form["token"]
    if "Bearer" not in token:
        token = f"Bearer {token}"
    if (
        len(token.split(" ")) != 2
    ):  # if the length is not 2, then it is not a valid token
        raise ValueError(f"Invalid token: {token}")
    if ";" in token or "&&" in token or "|" in token:
        raise ValueError(f"Invalid token: {token}")
    if not domain.endswith("/"):
        domain += "/"
    # set the domain in init.yaml
    config_response = update_regscale_config(str_param="domain", val=domain)
    if config_response != "Config updated":
        raise ValueError(f"Could not update domain in init.yaml: {config_response}")
    # login to the RegScale instance
    auth_token = login(token=token)
    logger.debug(f"Authenticated with {auth_token}")
    return redirect(url_for("home"))


@app.route("/upload_ssp", methods=["GET"])
def upload_ssp():
    """Upload a file for processing"""
    # Get list of catalogs
    regscale_catalogues = get_catgalogues()
    return render_template(
        "upload_ssp.html",
        regscale_catalogues=regscale_catalogues,
        site_info=get_site_info(),
    )


@app.route("/process_file", methods=["POST"])
def process_file():
    """process uploaded file"""
    file = request.files["file"]
    catalogue_id = request.form["regscale_catalogue_id"]
    filename = secure_filename(file.filename)
    default_csv_path = "./artifacts/import-results.csv"
    if os.path.exists(default_csv_path):
        os.remove(default_csv_path)
    artifacts_dir = "artifacts"
    file_path = os.path.join(artifacts_dir, filename)
    logger = create_logger()
    # Check if the file already exists and warn if needed
    if os.path.exists(file_path):
        # Logic to display a warning and handle overwrite (e.g., via user confirmation)
        pass

    # Save the file to the 'artifacts' directory
    file.save(file_path)

    # Call the existing function and get the CSV path and results
    csv_path, result_output, implementation_results = parse_and_load_xml_rev4(
        file_path=file_path, filename=filename, catalouge_id=catalogue_id
    )
    # Read and group the CSV data by error level (do this now as it is expensive)
    csv_data = pd.read_csv(csv_path)
    # if the csv file is not empty
    if not csv_data.empty:
        # group the csv data
        csv_data_grouped = (
            # sort the csv data by the model_layer and timestamp columns
            csv_data.sort_values(["model_layer", "timestamp"])
            # group the csv data by the level column
            .groupby("level")
            # convert dataframe to a dictionary and orient by the records
            .apply(lambda x: x.to_dict(orient="records"))
            # convert to a dictionary
            .to_dict()
        )
        value_counts = (
            # group the csv data by the level column
            csv_data.drop("timestamp", axis="columns")
            .drop("model_layer", axis="columns")
            .drop("record_type", axis="columns")
            .drop("event", axis="columns")
            .groupby("level")
            .agg(["count"])
            .to_dict()
        )
        value_counts["Results"] = value_counts.pop(("Unnamed: 0", "count"))
        category_counts = csv_data["record_type"].value_counts().to_dict()
        results = value_counts["Results"]
        # ensure that these exist as numbers
        if "Error" not in results:
            results["Error"] = 0
        if "Info" not in results:
            results["Info"] = 0
    else:
        logger.warning(f"{csv_path} is empty.")
        csv_data_grouped = {}
        results = {}
        category_counts = {}
        implementation_results = []
    # Render the success page with the grouped CSV data and result output
    return render_template(
        "upload_ssp_result.html",
        site_info=get_site_info(),
        csv_data_grouped=csv_data_grouped,
        results=results,
        result_output=result_output,
        category_counts=category_counts,
        filename=file.filename,
        implementation_results=len(implementation_results),
    )


@app.route("/make_base64", methods=["GET"])
def make_base64():
    """Form to upload a file to convert to base64 string"""
    return render_template("make_base64.html", site_info=get_site_info())


@app.route("/encode_base", methods=["POST"])
def encode_base64():
    """Return Base64-encoded string as file"""
    if request.method == "POST":
        # Check if the POST request has the file part
        if "file" not in request.files:
            return "No file part"
        file = request.files["file"]
        # If the user does not select a file, the browser submits an empty file without a filename.
        if file.filename == "":
            return "No selected file"

        if file:
            # Convert the uploaded file to Base64
            file_content = file.read()
            base64_content = base64.b64encode(file_content).decode("utf-8")

            # Create a filename for downloading
            download_filename = f"{file.filename}.txt"

            # Set up the response object for downloading
            response = Response(base64_content, content_type="text/plain")
            response.headers[
                "Content-Disposition"
            ] = f"attachment; filename={download_filename}"

            return response
    else:
        return render_template("make_base64.html", site_info=get_site_info())


def run_app(
    port: int = int(getenv("REGSCALE_FLASK_PORT", "5555")),
):
    """Run the CLI as a flask app
    :param int port: the port to serve flask on
    """
    Console().print(f"Running on http://127.0.0.1:{port}/")
    Console().print(f"Swagger docs at http://127.0.0.1:{port}/swagger/")
    Console().print("Press CTRL+C to quit")
    try:
        server = simple_server.make_server("0.0.0.0", port, app)
        server.serve_forever()
    except KeyboardInterrupt:
        Console().print("Exiting")

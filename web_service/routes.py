from flask import Blueprint, request, jsonify, redirect, url_for, render_template, current_app
import pylxd
import subprocess
import sys
import asyncio


#main_routes = Blueprint('main_routes', __name__, url_prefix='/jupyterhub-deploy/')
main_routes = Blueprint('main_routes', __name__)
client = pylxd.Client()

# Return the maximum number of containers to deploy at once
@main_routes.route('/max-deploy', methods=['GET'])
def max_deploy():
    return jsonify(current_app.config['MAX_DEPLOY'])

# Return app configuration data
@main_routes.route('/config', methods=['GET'])
def config():
    return jsonify(current_app.config)

# List existing container deploymenJayats
@main_routes.route('/list', methods=['GET'])
def list_hubs():
    containers = client.containers.all()
    hub_list = [{
        "name": c.name,
        "name": c.name, 
        "status": c.status,
        "description": c.config.get("user.description", "No description provided")
    } for c in containers if "jupyterhub" in c.name]
    return jsonify(hub_list)


# List only archived containers
@main_routes.route('/list-archived', methods=['GET'])
def list_archived_hubs():
    containers = client.containers.all()
    archived_list = [{
        "name": c.name,
        "name": c.name, 
        "status": c.status,
        "description": c.config.get("user.description", "No description provided")
    } for c in containers if c.name.startswith("jh-archive") and c.status.lower() == "stopped"]
    return jsonify(archived_list)


# Define an async function for creating containers
async def create_container(new_number, description, template_container_name='jh-template'):
    new_container_name = f"jupyterhub{new_number}"
    config = {
        'name': new_container_name,
        'source': {
            'type': 'copy',
            'source': template_container_name,
        },
        'config': {
            "user.description": description or f"JupyterHub instance {new_container_name}"
        }
    }
    new_container = client.instances.create(config, wait=True)
    new_container.start(wait=True)
    host_port = f"81{new_number}"
    new_container.devices.update({
        f"proxy-{host_port}": {
            "type": "proxy",
            "listen": f"tcp:0.0.0.0:{host_port}",
            "connect": "tcp:127.0.0.1:8000"
        }
    })
    new_container.save(wait=True)
    return new_container


@main_routes.route('/start', methods=['POST'])
async def start_hub():
    data = request.get_json()
    description = data.get('description')
    used_numbers = [int(c.name[-2:]) for c in client.containers.all() if "jupyterhub" in c.name]
    available_numbers = [i for i in range(1, current_app.config['MAX_DEPLOY']+1) if i not in used_numbers]
    if not available_numbers:
        return "No available slots for new JupyterHub instances", 400
    new_number = f"{available_numbers[0]:02d}"
    
    container = await create_container(new_number, description)
    return jsonify(f"/jupyterhub{new_number}"), 200


# Deploy an archived container
@main_routes.route('/deploy-archived/<hub_name>', methods=['POST'])
def deploy_archived_hub(hub_name):
    used_numbers = [int(c.name[-2:]) for c in client.containers.all() if "jupyterhub" in c.name and c.name[-2:].isdigit()]
    available_numbers = [i for i in range(1, current_app.config['MAX_DEPLOY']+1) if i not in used_numbers]

    if not available_numbers:
        return "No available slots for deploying archived JupyterHub instances", 400

    new_number = f"{available_numbers[0]:02d}"
    new_container_name = f"jupyterhub{new_number}"

    try:
        container = client.containers.get(hub_name)
        if container.status.lower() == "stopped":
            # Rename archived container to a new jupyterhub name
            container.rename(new_container_name, wait=True)
            #container.config["user.description"] = f"JupyterHub instance {new_container_name} (restored from archive)"
            container.save(wait=True)
            container.start(wait=True)

            # Add LXD proxy device to map container port 8000 to host port 80xx
            host_port = f"81{new_number}"
            container.devices.update({
                f"proxy-{host_port}": {
                    "type": "proxy",
                    "listen": f"tcp:0.0.0.0:{host_port}",
                    "connect": "tcp:127.0.0.1:8000"
                }
            })
            container.save(wait=True)

            return f"{new_container_name} has been deployed.", 200
        else:
            return f"{hub_name} is not stopped.", 400
    except pylxd.exceptions.NotFound:
        return f"Container {hub_name} not found.", 404


# Stop a running container
@main_routes.route('/stop/<hub_name>', methods=['POST'])
def stop_hub(hub_name):
    try:
        container = client.containers.get(hub_name)
        if container.status.lower() == "running":
            container.stop(wait=True)
            return f"{hub_name} has been stopped.", 200
        return f"{hub_name} is not running.", 400
    except pylxd.exceptions.NotFound:
        return f"Container {hub_name} not found.", 404

# Check if an archive tag is available
@main_routes.route('/check-archive-tag/<tag>', methods=['GET'])
def check_archive_tag(tag):
    archive_name = f"jh-archive-{tag}"
    containers = client.containers.all()
    exists = any(container.name == archive_name for container in containers)
    return jsonify({"exists": exists})

# Archive a stopped container
@main_routes.route('/archive/<hub_name>', methods=['POST'])
def archive_hub(hub_name):
    data = request.get_json(silent=True)
    print(f'request json: {data}', file=sys.stderr)
    tag = data.get('tag')
    if not tag:
        return "Tag is required", 400
    if data is None:
        return "Invalid JSON payload", 400
        return "Tag is required", 400

    archive_name = f"jh-archive-{tag}"
    containers = client.containers.all()
    if any(container.name == archive_name for container in containers):
        return f"Archive name {archive_name} already exists.", 400

    try:
        container = client.containers.get(hub_name)
        if container.status.lower() == "stopped":
            container.rename(archive_name, wait=True)
            #container.config["user.description"] = f"Archived JupyterHub instance with tag: {tag}"
            container.save(wait=True)
            return f"{hub_name} has been archived as {archive_name}.", 200
        return f"Container {hub_name} is not stopped and cannot be archived.", 400
    except pylxd.exceptions.NotFound:
        return f"Container {hub_name} not found.", 404

# Front end (app root path)
@main_routes.route('/')
def index():
    return render_template('index.html')



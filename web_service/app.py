from flask import Flask, request, jsonify, redirect, url_for, render_template
import pylxd
import subprocess
import sys

app = Flask(__name__)
client = pylxd.Client()

# List existing container deployments
@app.route('/list', methods=['GET'])
def list_hubs():
    containers = client.containers.all()
    #print([c.name for c in containers], file=sys.stderr)
    hub_list = [{"name": c.name, "status": c.status} for c in containers if "jupyterhub" in c.name]
    return jsonify(hub_list)

# Start a new JupyterHub container
@app.route('/start', methods=['POST'])
def start_hub():
    # Find available "xx" value
    used_numbers = [int(c.name[-2:]) for c in client.containers.all() if "jupyterhub" in c.name]
    available_numbers = [i for i in range(1, 11) if i not in used_numbers]
    
    print(f'used_numbers: {used_numbers}', file=sys.stderr) # debug
    print(f'available_numbers: {available_numbers}', file=sys.stderr) # debug

    if not available_numbers:
        return "No available slots for new JupyterHub instances", 400

    new_number = f"{available_numbers[0]:02d}"
    new_container_name = f"jupyterhub{new_number}"

    ## Copy the template
    #template = client.containers.get("jh-template")
    #new_container = template.copy(new_container_name, wait=True)

    # Create a new container using the template container configuration
    template_container_name = "jh-template"
    config = {
        'name': new_container_name,
        'source': {
            'type': 'copy',
            'source': template_container_name,
        }
    }
    new_container = client.instances.create(config, wait=True)
    
    # Start the new container
    new_container.start(wait=True)

    # Add LXD proxy device to map container port 8000 to host port 80xx
    host_port = f"80{new_number}"
    new_container.devices.update({
        f"proxy-{host_port}": {
            "type": "proxy",
            "listen": f"tcp:0.0.0.0:{host_port}",
            "connect": "tcp:127.0.0.1:8000"
        }
    })

    # Reload NGINX to apply new configuration (assuming you have an NGINX template to include new paths)
    subprocess.run(["sudo", "nginx", "-s", "reload"])

    # Redirect to the new JupyterHub instance
    return redirect(f"/jupyterhub{new_number}")

# Stop an existing container
@app.route('/stop/<hub_id>', methods=['POST'])
def stop_hub(hub_id):
    container = client.containers.get(hub_id)
    if container.status == "Running":
        container.stop(wait=True)
    return f"Stopped {hub_id}"

# Front end (app root path)
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='localhost', port=5000)

#!/bin/bash
cp -R ../jupyterhub-container-deploy /opt
cd /opt/jupyterhub-container-deploy
rm -rf .venv # just for testing
python3 -m venv /opt/jupyterhub-container-deploy/.venv
#source /opt/jupyterhub-container-deploy/.venv/bin/activate
#env
/opt/jupyterhub-container-deploy/.venv/bin/python3 -m pip install -r requirements.txt
cp ./scripts/jupyterhub-container-deploy.service /etc/systemd/system/jupyterhub-container-deploy.service
systemctl enable jupyterhub-container-deploy
systemctl start jupyterhub-container-deploy
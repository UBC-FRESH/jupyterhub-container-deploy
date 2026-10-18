"""Development and WSGI entry point for the deployment service.

Run it directly with ``python run.py`` for a local server, or point ``gunicorn`` at the
module-level ``app`` object, as the systemd unit does::

    gunicorn -b 127.0.0.1:5000 run:app
"""

from __future__ import annotations

import os

from web_service import create_app

app = create_app()

if __name__ == "__main__":
    app.run(
        host=os.environ.get("JHD_HOST", "127.0.0.1"),
        port=int(os.environ.get("JHD_PORT", "5000")),
    )

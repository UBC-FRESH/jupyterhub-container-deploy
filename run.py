from web_service import create_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = create_app()

# Configure DispatcherMiddleware
#app.wsgi_app = DispatcherMiddleware(app, {'/jupyterhub-deploy': app})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
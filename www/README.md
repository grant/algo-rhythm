# Flask web server with React + Socket.io frontend

## Tech

These are the tools you'll need to develop on this repo.

### Backend (python)
- [Flask](http://flask.pocoo.org/) - Web Server
- [socket.io](https://github.com/miguelgrinberg/Flask-SocketIO) - Send notifications to users

### Frontend (React)
- [React](https://facebook.github.io/react/) - Client UI
- [socket.io](http://socket.io/) - Receives notifications, sends user actions.
- [Babel](https://babeljs.io/docs/learn-es2015/) - Better JS syntax
- [Webpack](https://webpack.github.io/) - Bundles files into one bundle.js file
- [npm](https://www.npmjs.com/) - Some external libraries
- Plain CSS (for now)

### Architecture

Basically, the site flow works like this:
- A user hits the Flask home page at / and gets a plain `index.html` with a webpacked `bundle.js`
- The `bundle.js` then loads all of HTML for the page given the current data it has (none). It also sets up a websocket connection.
- On client updates all of the UI whenever it gets a push event called `status` from `socket.io`.
  - On websocket connection success, the server pushes the first `status` event.
  - When our server has an update handler called for the backend, it sends a broadcast to the clients to update about the new status.

## Install Instructions

Open two terminal windows:

1. Run server
2. Run clint build

While developing, check both terminals for errors.

### Run Server

```sh
# Install
pip install -r ../requirements.txt

# Start server (will be exposed)
sudo python server.py

# Open the site
open http://0.0.0.0:80/
```

### Run client

```sh
npm i
npm run dev
```

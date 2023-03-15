from website import create_app
from waitress import serve

app = create_app()

if __name__ == '__main__':
    # Run app with debug mode
    app.run(debug=True, port=8222)
    # Serve app with waitress
    # serve(app, host="0.0.0.0", port=8222)
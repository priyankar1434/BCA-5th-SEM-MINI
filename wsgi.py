from app import app

if __name__ == "__main__":
    # This block is only for local development
    # In production, Gunicorn will import this module
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

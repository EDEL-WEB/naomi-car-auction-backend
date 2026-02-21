import os
from dotenv import load_dotenv
from app import create_app, socketio

load_dotenv()
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # Start scheduler only in main process
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or os.getenv("FLASK_ENV") != "development":
        from app.utils.scheduler import start_scheduler
        start_scheduler(app)
        app.logger.info("Scheduler started in main process")

    socketio.run(
        app,
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_ENV', 'development') == 'development'
    )
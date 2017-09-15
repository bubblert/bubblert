#!/usr/bin/env python
import threading
from app import socketio, app, celery


if __name__ == '__main__':
    app_thread = threading.Thread(target=lambda: socketio.run(app, port=5000), daemon=True)
    # celery_thread = threading.Thread(target=lambda: celery.start(argv=['celery', 'worker', '-l', 'info']), daemon=True)
    # celery_thread.start()

    app_thread.start()

    app_thread.join()
    # celery_thread.join()


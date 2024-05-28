from .tasks import update_trash_data
from .firebase_config import initialize_firebase

# Listener function
def stream_handler():
    database = initialize_firebase()

    def inner(message):
        update_trash_data.delay()  # Trigger Celery task on data change

    # Start listening for changes in the 'TrashData' node
    my_stream = database.child("TrashData").stream(inner)
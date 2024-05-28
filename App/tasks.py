# myapp/tasks.py
from celery import shared_task
from .models import Trashdata
from .firebase_config import initialize_firebase

@shared_task
def update_trash_data():
    database = initialize_firebase()

    # Fetch data from Firebase Realtime Database
    location = database.child('TrashData').child('location').get().val()
    trash = database.child('TrashData').child('trash').get().val()

    # Update or create the data in the Django model
    Trashdata.objects.update_or_create(
        id=1,  # Assuming a single entry for simplicity; adjust as needed
        defaults={'location': location, 'trash': trash}
    )
import pyrebase

def initialize_firebase():
    config = {
        "apiKey": "AIzaSyB9w1Ib0MKPTtNeEp709TllbPbyTZSIQ8A",
        "authDomain": "gts-project-4020e.firebaseapp.com",
        "databaseURL": "https://gts-project-4020e-default-rtdb.asia-southeast1.firebasedatabase.app",
        "projectId": "gts-project-4020e",
        "storageBucket": "gts-project-4020e.appspot.com",
        "messagingSenderId": "931015405980",
        "appId": "1:931015405980:web:25416f1af917aaf1cfd859",
        "measurementId": "G-Q9K4LTZQKF"
    }

    firebase = pyrebase.initialize_app(config)
    return firebase.database()


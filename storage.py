import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
from lib.models import Scrobble, Track, Artist
from typing import List, Optional

class FireStoreHelper:

    def __init__(self,root_collection: str):
        cred = credentials.Certificate('serviceAccountSecret.json')
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()
        self.root_collection = self.db.collection(root_collection)

    
    def save_user_scrobbles(self, username: str, scrobbles: List[Scrobble], last_update: int) -> bool:
        user_doc_ref = self.root_collection.document(username)
        user_scrobbles_ref = user_doc_ref.collection('scrobbles')
        batch = self.db.batch()
        # save from list in slices of 500
        s,n,i = 0,500,500
        while s < len(scrobbles):
            for scrobble in scrobbles[s:n]:
                doc_ref=user_scrobbles_ref.document(str(hash(scrobble)))
                batch.set(doc_ref,scrobble.dict)
            s,n=n,n+i
            batch.commit()
        user_doc_ref.set({'last_update':last_update})
        return True


    def get_all_user_scrobbles(self, username: str) ->  List[Scrobble]:
        user_doc_ref = self.root_collection.document(username)
        user_scrobbles = user_doc_ref.collection('scrobbles').get()
        result: List[Scrobble] = []
        for s in user_scrobbles:
            temp = Scrobble.from_dict(s.to_dict())
            result.append(temp)
        print(result)
        return result    

fs = FireStoreHelper("users")
test_track = Track("Rumors",artist_name="R3hab",album_name="The Wave")
test_scrobble = Scrobble(track=test_track,date=int(datetime.now().timestamp()))
scrobs = [test_scrobble]
fs.save_user_scrobbles('user',scrobs,int(datetime.now().timestamp()))
fs.get_all_user_scrobbles('user')

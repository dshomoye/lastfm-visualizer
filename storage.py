import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
from lib.models import Scrobble, Track, Artist
from typing import List, Optional, Dict, Any

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


    def get_all_user_scrobbles(self, username: str) ->  dict:
        user_doc_ref = self.root_collection.document(username)
        user_scrobbles = user_doc_ref.collection('scrobbles').get()
        result_list: List[Scrobble] = []
        for s in user_scrobbles:
            temp = Scrobble.from_dict(s.to_dict())
            result_list.append(temp)
        last_update: int = int(user_doc_ref.get().to_dict()['last_update'])
        result: Dict[str, Any]={}
        result['scrobbles'] = result_list
        result['last_udpate'] = last_update
        return result    
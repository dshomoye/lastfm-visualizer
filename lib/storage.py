import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
from lib.models import Scrobble, Track, Artist
from typing import List, Optional, Dict, Any
from lib.errors import FireStoreLimitExceedError
from google.cloud.exceptions import NotFound as NotFoundInFireStore

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
        s,n,i = 0,450,450
        size: int = len(scrobbles)
        if size > 20000: raise FireStoreLimitExceedError("The size of scrobble exceeds the free tier for fire store ☹️")
        while s < len(scrobbles):
            for scrobble in scrobbles[s:n]:
                doc_ref=user_scrobbles_ref.document(str(hash(scrobble)))
                batch.set(doc_ref,scrobble.dict)
            s,n=n,n+i
            batch.commit()
        if last_update: user_doc_ref.set({'last_update':last_update})
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
    

    def get_user_scrobles_in_period(self,username: str, start_period: datetime, end_period: datetime) -> List[Scrobble]:
        user_scrobbles_ref = self.__get_user_scrobbles_ref(username)
        query_ref = user_scrobbles_ref.where('date', '>=', start_period).where('date', '<=', end_period)
        result = query_ref.get()
        #result_list: List[Scrobble] = []
        result_list: List[Scrobble] = list((
            Scrobble.from_dict(s.to_dict()) for s in result
        ))
        '''
        for s in result:
            t = Scrobble.from_dict(s.to_dict())
            result_list.append(t)'''
        return result_list
    
    def check_user_in_db(self,username: str) -> bool:
        try:
            user_doc_ref = self.root_collection.document(username)
            last_udpate = user_doc_ref.get().to_dict()
            return last_udpate is not None
        except NotFoundInFireStore:
            return False
    
    def get_last_scrobble_update(self,username: str):
        user_doc_ref = self.root_collection.document(username)
        last_update: int = int(user_doc_ref.get().to_dict()['last_update'])
        return last_update
        
    def __get_user_scrobbles_ref(self,username: str):
        user_doc_ref = self.root_collection.document(username)
        return user_doc_ref.collection('scrobbles')
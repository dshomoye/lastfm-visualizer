class ScrobbleFetchFailed(Exception):
    pass


class LastFMUserNotFound(Exception):
    pass


class FireStoreError(Exception):
    pass


class FireStoreLimitExceedError(FireStoreError):
    pass

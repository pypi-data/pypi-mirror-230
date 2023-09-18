import threading


class SessionManager:
    """
    Factory class intended for better session control.
    Example of usage:
    def get_session_manager():
        return SessionManager(SessionMaker: sqlalchemy.orm.sessionmaker)
    """

    def __init__(self, session_factory):
        self._current_session = None
        self._current_thread_id = None
        self._session_factory = session_factory

    def get_session(self):
        thread_id = threading.current_thread().ident
        if thread_id != self._current_thread_id:
            if self._current_session:
                self._current_session.close()
            self._current_session = self._session_factory()
            self._current_thread_id = thread_id
        return self._current_session

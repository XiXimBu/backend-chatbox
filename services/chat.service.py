from helper.import_helper import load_module

llm = load_module("llm_service", "services", "llm.service.py")
chat_repo = load_module("chat_repository", "repositories", "chat.repository.py")


class ChatService:
    def __init__(self):
        self._sessions: dict[str, object] = {}
        self._session_config: dict[str, tuple[str, str]] = {}

    def _drop_cached_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
        self._session_config.pop(session_id, None)

    def _get_session(self, session_id: str, level: str, topic: str):
        cached = self._session_config.get(session_id)
        if cached and cached != (level, topic):
            self._drop_cached_session(session_id)

        if session_id not in self._sessions:
            history = chat_repo.chat_repository.get_history(session_id)
            gemini_history = llm.build_gemini_history(history) if history else None
            self._sessions[session_id] = llm.create_chat_session(
                level=level,
                topic=topic,
                history=gemini_history,
            )
            self._session_config[session_id] = (level, topic)

        return self._sessions[session_id]

    def send_message(
        self,
        session_id: str,
        message: str,
        level: str = "basic",
        topic: str = "python",
    ) -> str:
        chat_repo.chat_repository.get_or_create_session(session_id, level, topic)

        chat = self._get_session(session_id, level, topic)
        response = chat.send_message(message)
        reply = response.text

        chat_repo.chat_repository.save_message(session_id, "user", message)
        chat_repo.chat_repository.save_message(session_id, "assistant", reply)
        return reply

    def clear_history(self, session_id: str) -> None:
        self._drop_cached_session(session_id)
        chat_repo.chat_repository.clear_history(session_id)


chat_service = ChatService()

from helper.import_helper import load_module

llm = load_module("llm_service", "services", "llm.service.py")
chat_repo = load_module("chat_repository", "repositories", "chat.repository.py")


class ChatService:
    def send_message(
        self,
        session_id: str,
        message: str,
        level: str = "basic",
        topic: str = "python",
    ) -> str:
        chat_repo.chat_repository.get_or_create_session(session_id, level, topic)

        history = chat_repo.chat_repository.get_history(session_id)
        gemini_history = llm.build_gemini_history(history) if history else None

        reply = llm.send_message(level, topic, gemini_history, message)

        chat_repo.chat_repository.save_message(session_id, "user", message)
        chat_repo.chat_repository.save_message(session_id, "assistant", reply)
        return reply

    def clear_history(self, session_id: str) -> None:
        chat_repo.chat_repository.clear_history(session_id)


chat_service = ChatService()

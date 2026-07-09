# brain/conversation_memory.py

class ConversationMemory:

    def __init__(self):
        self.recent_topics = []

    def remember(self, topic):
        self.recent_topics.append(topic)

        if len(self.recent_topics) > 20:
            self.recent_topics.pop(0)

    def get_recent_topics(self):
        return self.recent_topics
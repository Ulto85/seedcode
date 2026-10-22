class VoteTracker:
    def __init__(self):
        pass

    def vote(self, user_id: str, article_id: str, vote: str) -> str:
        pass

    def get_last_votes(self, user_id: str) -> list:
        pass

    # ---- Follow-up ----
    def score(self, article_id: str) -> int:
        pass

    def top_article(self):
        pass

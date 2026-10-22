class ReferralNetwork:
    def __init__(self):
        pass

    def add_user(self, user_id: str) -> bool:
        pass

    def add_referral(self, referrer: str, candidate: str) -> bool:
        pass

    def get_direct_referrals(self, user_id: str) -> list:
        pass

    # Part 2
    def total_referral_count(self, user_id: str) -> int:
        pass

    def top_referrers_by_reach(self, k: int) -> list:
        """List of [user_id, reach], best first."""
        pass

    # Follow-up
    def flow_centrality(self, user_id: str) -> int:
        pass

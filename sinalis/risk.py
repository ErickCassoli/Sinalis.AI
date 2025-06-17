"""Risk management utilities."""

class RiskManager:
    """Simple risk manager with martingale and daily stop."""

    def __init__(self, daily_stop: float = 250.0, martingale_limit: int = 2):
        self.daily_stop = daily_stop
        self.martingale_limit = martingale_limit
        self.daily_loss = 0.0
        self.martingale_count = 0

    def update(self, last_result: str) -> bool:
        """Update counters and return if trading can continue."""
        if last_result == "loss":
            self.martingale_count = min(
                self.martingale_count + 1, self.martingale_limit
            )
            self.daily_loss += 1  # placeholder
        elif last_result == "win":
            self.martingale_count = 0
        return self.daily_loss < self.daily_stop

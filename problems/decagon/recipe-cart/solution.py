from collections import Counter


class RecipeCart:
    """Stores an operation log (space O(#versions)) and keeps live ingredient totals.
    checkout(v) replays the first v ops: O(v * recipe_size)."""

    def __init__(self, recipes: dict, deals: dict):
        self.recipes = recipes
        self.deals = deals
        self.ops = []                 # ops[i] produced version i + 1
        self.counts = Counter()       # recipe -> copies in cart
        self.totals = Counter()       # ingredient -> quantity in cart

    def _apply(self, kind, name):
        sign = 1 if kind == "add" else -1
        self.counts[name] += sign
        if self.counts[name] == 0:
            del self.counts[name]
        for ing, q in self.recipes[name].items():
            self.totals[ing] += sign * q

    def add_recipe(self, name: str) -> bool:
        if name not in self.recipes:
            return False
        self.ops.append(("add", name))
        self._apply("add", name)
        return True

    def remove_recipe(self, name: str) -> bool:
        if self.counts[name] == 0:
            return False
        self.ops.append(("remove", name))
        self._apply("remove", name)
        return True

    def get_total_discounts(self) -> int:
        total = 0
        for ing, (size, off) in self.deals.items():
            total += self.totals[ing] // size * off
        return total

    def get_version(self) -> int:
        return len(self.ops)

    def checkout(self, version: int) -> bool:
        if not 0 <= version <= len(self.ops):
            return False
        ops = self.ops[:version]
        self.ops, self.counts, self.totals = [], Counter(), Counter()
        for kind, name in ops:
            self.ops.append((kind, name))
            self._apply(kind, name)
        return True

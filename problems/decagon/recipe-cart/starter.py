class RecipeCart:
    def __init__(self, recipes: dict, deals: dict):
        pass

    def add_recipe(self, name: str) -> bool:
        pass

    def remove_recipe(self, name: str) -> bool:
        pass

    def get_total_discounts(self) -> int:
        pass

    # ---- Follow-up ----
    def get_version(self) -> int:
        pass

    def checkout(self, version: int) -> bool:
        pass

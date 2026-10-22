---
title: Versioned Recipe Cart
difficulty: Medium
source: Decagon SWE phone screen, "Cooking App Cart" (most reported, 2026)
order: 1
minutes: 45
tags: design, hash map, versioning
---
You're building the cart for a cooking app. Users add **recipes** to their cart, and each recipe needs a set of
ingredients. Ingredients are bought in bulk across the whole cart, and some have **bulk deals**.

```
recipes: dict[str, dict[str, int]]   # recipe -> {ingredient: quantity}
deals:   dict[str, list[int]]        # ingredient -> [bulk_size, discount]
```

A deal `[bulk_size, discount]` means: for every *full* group of `bulk_size` units of that ingredient in the cart
(summed across all recipes), you save `discount`, i.e. `total_qty // bulk_size * discount`.

### Part 1
```
RecipeCart(recipes, deals)
add_recipe(name) -> bool          # False if the recipe is unknown. The same recipe can be added more than once.
remove_recipe(name) -> bool       # Removes ONE copy. False if it isn't in the cart.
get_total_discounts() -> int
```

### Follow-up: versioning
The cart starts at version `0`. Every **successful** `add_recipe` / `remove_recipe` creates a new version (failed
calls don't).
```
get_version() -> int              # the current version number
checkout(version) -> bool         # restore the cart to that version; False (and no change) if it doesn't exist
```
After `checkout(v)`, every version newer than `v` is **discarded**, and the next change creates version `v + 1`.
```
v0: {}          add pasta -> v1: {pasta}     add soup -> v2: {pasta, soup}
checkout(1)  -> cart is {pasta}; v2 is gone, so checkout(2) now returns False
add omelet   -> v2: {pasta, omelet}
```

### What the interviewer cares about
- **Space efficiency:** don't store a full copy of the cart for every version (store operations and replay, or deltas)
- Clean class design and edge cases: unknown recipe, removing something not in the cart, invalid checkout
- Some interviewers ask for `undo()` / `redo()` instead of versioning. It's the same idea: an operation log plus a pointer.

*Test inputs use 5 recipes: pasta, salad, pizza, soup, omelet. "ghost" and "unicorn" are unknown recipes.*

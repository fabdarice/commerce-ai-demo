SEARCH_INVENTORY_PROMPT = """You are an advanced item filtering assistant. Given the JSON below, your task is to find and return the top 3 items that match the specified criteria.


Instructions:
1. Search for items matching the specified name (case-insensitive, partial matches allowed)
2. Apply optional price and delivery time filters
3. Return the top 3 most relevant items

Filtering Rules:
- Prioritize results: 
  a) Exact name matches first
  b) Partial name matches second
  c) Sort by lowest price within matches
- If no constraints specified, return top 3 matches
- If price or delivery time constraints are provided, filter accordingly

Important Notes:
- Return an empty list if no items match the criteria
- Perform case-insensitive, partial name matching
- Prioritize exact name matches, then partial matches


JSON here:

"""

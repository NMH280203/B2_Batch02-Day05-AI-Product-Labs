from __future__ import annotations

import os
from pathlib import Path
from typing import Any
import yaml
from google.genai import types

# Import underlying tool implementations
from .weather.tool import handle as handle_weather
from .food_search.tool import handle as handle_food_search
from .places.tool import handle_search as handle_places_search, handle_detail as handle_places_detail
from .ranking.tool import handle as handle_ranking
from .scraper.tool import crawl_trending_foods, crawl_restaurant_reviews

# Mapping of tool name -> async handler function
TOOL_HANDLERS = {
    "get_weather": handle_weather,
    "search_food_by_criteria": handle_food_search,
    "search_nearby_restaurants": handle_places_search,
    "get_restaurant_detail": handle_places_detail,
    "rank_restaurants": handle_ranking,
    "crawl_trending_foods": crawl_trending_foods,
    "crawl_restaurant_reviews": crawl_restaurant_reviews,
}


def load_tool_declarations() -> list[dict[str, Any]]:
    """Loads all tool declarations from artifacts/tools.yaml."""
    base_dir = Path(__file__).parent.parent
    path = base_dir / "artifacts" / "tools.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Tools declarations not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["tools"]


def to_gemini_tools(filter_names: list[str]) -> list[types.Tool]:
    """
    Loads declarations from tools.yaml, filters them by name, 
    and returns a list containing a google.genai.types.Tool with FunctionDeclarations.
    """
    declarations = load_tool_declarations()
    function_declarations = []
    
    for item in declarations:
        if item["name"] in filter_names:
            # Map type to uppercase schema standard for Gemini API
            params = item.get("parameters", {"type": "object", "properties": {}})
            
            # Helper to recursively fix types for Gemini SDK schema
            def sanitize_schema(schema: dict) -> dict:
                if not isinstance(schema, dict):
                    return schema
                sanitized = dict(schema)
                if "type" in sanitized:
                    sanitized["type"] = sanitized["type"].upper()
                if "properties" in sanitized:
                    sanitized["properties"] = {
                        k: sanitize_schema(v) for k, v in sanitized["properties"].items()
                    }
                if "items" in sanitized:
                    sanitized["items"] = sanitize_schema(sanitized["items"])
                return sanitized

            sanitized_params = sanitize_schema(params)

            function_declarations.append(
                types.FunctionDeclaration(
                    name=item["name"],
                    description=item.get("description", ""),
                    parameters=sanitized_params,
                )
            )
            
    return [types.Tool(function_declarations=function_declarations)] if function_declarations else []

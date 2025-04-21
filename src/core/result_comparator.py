from typing import Dict, Any, List, Union
from .parallel_config import AgentVersion
import json

class ResultComparator:
    """Compare results from different versions of agents"""
    
    def __init__(self):
        self.comparison_keys = {
            "title": "Title",
            "author": "Author",
            "year": "Year",
            "content_summary": "Content Summary",
            "analysis": {
                "themes": "Themes",
                "characters": "Characters",
                "plot_points": "Plot Points"
            }
        }

    def compare(self, original: Any, mcp: Any) -> Dict[str, Any]:
        """Compare original and MCP results"""
        if original is None and mcp is None:
            return {"status": "both_failed", "details": "Both versions failed to produce results"}
        elif original is None:
            return {"status": "original_failed", "details": "Original version failed"}
        elif mcp is None:
            return {"status": "mcp_failed", "details": "MCP version failed"}
        
        if isinstance(original, dict) and isinstance(mcp, dict):
            return self._compare_dicts(original, mcp)
        elif isinstance(original, list) and isinstance(mcp, list):
            return self._compare_lists(original, mcp)
        else:
            return {
                "status": "different_types",
                "original_type": type(original).__name__,
                "mcp_type": type(mcp).__name__,
                "original": str(original),
                "mcp": str(mcp)
            }

    def _compare_dicts(self, original: Dict[str, Any], mcp: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two dictionaries"""
        result = {
            "status": "identical",
            "differences": {},
            "missing_in_original": [],
            "missing_in_mcp": [],
            "extra_in_original": [],
            "extra_in_mcp": []
        }
        
        # Compare keys present in both
        for key in set(original.keys()) & set(mcp.keys()):
            if original[key] != mcp[key]:
                result["status"] = "different"
                result["differences"][key] = {
                    "original": original[key],
                    "mcp": mcp[key]
                }
        
        # Check for missing keys
        for key in set(mcp.keys()) - set(original.keys()):
            result["status"] = "different"
            result["missing_in_original"].append(key)
        
        for key in set(original.keys()) - set(mcp.keys()):
            result["status"] = "different"
            result["missing_in_mcp"].append(key)
        
        return result

    def _compare_lists(self, original: List[Any], mcp: List[Any]) -> Dict[str, Any]:
        """Compare two lists"""
        result = {
            "status": "identical",
            "differences": [],
            "missing_in_original": [],
            "missing_in_mcp": []
        }
        
        if len(original) != len(mcp):
            result["status"] = "different"
            result["differences"].append({
                "type": "length_mismatch",
                "original_length": len(original),
                "mcp_length": len(mcp)
            })
        
        # Compare elements
        for i, (orig_item, mcp_item) in enumerate(zip(original, mcp)):
            if orig_item != mcp_item:
                result["status"] = "different"
                result["differences"].append({
                    "index": i,
                    "original": orig_item,
                    "mcp": mcp_item
                })
        
        return result

    def get_summary(self, comparison: Dict[str, Any]) -> str:
        """Get human-readable summary of comparison"""
        if comparison["status"] == "identical":
            return "Results are identical"
        
        summary = []
        if comparison["status"] == "different":
            if "differences" in comparison:
                for key, diff in comparison["differences"].items():
                    summary.append(f"Different {key}:")
                    summary.append(f"  Original: {diff['original']}")
                    summary.append(f"  MCP: {diff['mcp']}")
            
            if comparison.get("missing_in_original"):
                summary.append("Missing in original version:")
                summary.extend(f"  - {key}" for key in comparison["missing_in_original"])
            
            if comparison.get("missing_in_mcp"):
                summary.append("Missing in MCP version:")
                summary.extend(f"  - {key}" for key in comparison["missing_in_mcp"])
        
        return "\n".join(summary) 
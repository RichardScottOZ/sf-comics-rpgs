import pytest
from src.core.result_comparator import ResultComparator

def test_compare_identical_results():
    """Test comparing identical results"""
    comparator = ResultComparator()
    original = {"data": "test", "count": 5}
    mcp = {"data": "test", "count": 5}
    
    comparison = comparator.compare_results(original, mcp)
    
    assert comparison["identical"] is True
    assert comparison["differences"] == []
    assert comparison["original_keys"] == ["data", "count"]
    assert comparison["mcp_keys"] == ["data", "count"]
    assert comparison["common_keys"] == ["data", "count"]
    assert comparison["missing_in_original"] == []
    assert comparison["missing_in_mcp"] == []

def test_compare_different_results():
    """Test comparing different results"""
    comparator = ResultComparator()
    original = {"data": "test", "count": 5}
    mcp = {"data": "different", "count": 10}
    
    comparison = comparator.compare_results(original, mcp)
    
    assert comparison["identical"] is False
    assert len(comparison["differences"]) == 2
    assert comparison["original_keys"] == ["data", "count"]
    assert comparison["mcp_keys"] == ["data", "count"]
    assert comparison["common_keys"] == ["data", "count"]
    assert comparison["missing_in_original"] == []
    assert comparison["missing_in_mcp"] == []

def test_compare_missing_keys():
    """Test comparing results with missing keys"""
    comparator = ResultComparator()
    original = {"data": "test", "count": 5}
    mcp = {"data": "test", "extra": "value"}
    
    comparison = comparator.compare_results(original, mcp)
    
    assert comparison["identical"] is False
    assert "count" in comparison["missing_in_mcp"]
    assert "extra" in comparison["missing_in_original"]
    assert comparison["common_keys"] == ["data"]

def test_compare_nested_structures():
    """Test comparing nested data structures"""
    comparator = ResultComparator()
    original = {
        "data": {
            "nested": {
                "value": 1,
                "array": [1, 2, 3]
            }
        }
    }
    mcp = {
        "data": {
            "nested": {
                "value": 2,
                "array": [1, 2, 4]
            }
        }
    }
    
    comparison = comparator.compare_results(original, mcp)
    
    assert comparison["identical"] is False
    assert len(comparison["differences"]) > 0
    assert "data.nested.value" in [d["key"] for d in comparison["differences"]]
    assert "data.nested.array" in [d["key"] for d in comparison["differences"]]

def test_compare_with_none_values():
    """Test comparing results with None values"""
    comparator = ResultComparator()
    original = {"data": None, "count": 5}
    mcp = {"data": "test", "count": None}
    
    comparison = comparator.compare_results(original, mcp)
    
    assert comparison["identical"] is False
    assert len(comparison["differences"]) == 2
    assert "data" in [d["key"] for d in comparison["differences"]]
    assert "count" in [d["key"] for d in comparison["differences"]]

def test_compare_with_empty_structures():
    """Test comparing empty data structures"""
    comparator = ResultComparator()
    original = {}
    mcp = {}
    
    comparison = comparator.compare_results(original, mcp)
    
    assert comparison["identical"] is True
    assert comparison["differences"] == []
    assert comparison["original_keys"] == []
    assert comparison["mcp_keys"] == []
    assert comparison["common_keys"] == []
    assert comparison["missing_in_original"] == []
    assert comparison["missing_in_mcp"] == []

def test_compare_with_error_results():
    """Test comparing results containing error information"""
    comparator = ResultComparator()
    original = {"error": "Original error", "status": "failed"}
    mcp = {"error": "MCP error", "status": "failed"}
    
    comparison = comparator.compare_results(original, mcp)
    
    assert comparison["identical"] is False
    assert "error" in [d["key"] for d in comparison["differences"]]
    assert comparison["common_keys"] == ["status"]

def test_compare_with_different_types():
    """Test comparing results with different value types"""
    comparator = ResultComparator()
    original = {"data": 123, "count": "5"}
    mcp = {"data": "123", "count": 5}
    
    comparison = comparator.compare_results(original, mcp)
    
    assert comparison["identical"] is False
    assert len(comparison["differences"]) == 2
    assert "data" in [d["key"] for d in comparison["differences"]]
    assert "count" in [d["key"] for d in comparison["differences"]]

def test_compare_with_arrays():
    """Test comparing results with arrays"""
    comparator = ResultComparator()
    original = {"data": [1, 2, 3], "items": ["a", "b", "c"]}
    mcp = {"data": [1, 2, 4], "items": ["a", "b", "d"]}
    
    comparison = comparator.compare_results(original, mcp)
    
    assert comparison["identical"] is False
    assert len(comparison["differences"]) == 2
    assert "data" in [d["key"] for d in comparison["differences"]]
    assert "items" in [d["key"] for d in comparison["differences"]] 
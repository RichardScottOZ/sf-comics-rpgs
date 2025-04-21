import pytest
from src.core.result_comparator import ResultComparator

def test_compare_simple_dicts():
    comparator = ResultComparator()
    dict1 = {'a': 1, 'b': 2}
    dict2 = {'a': 1, 'b': 3}
    
    result = comparator.compare(dict1, dict2)
    assert 'identical' in result
    assert 'different' in result
    assert 'missing' in result
    assert 'extra' in result
    
    assert 'a' in result['identical']
    assert 'b' in result['different']
    assert not result['missing']
    assert not result['extra']

def test_compare_nested_dicts():
    comparator = ResultComparator()
    dict1 = {'a': {'b': 1, 'c': 2}, 'd': 3}
    dict2 = {'a': {'b': 1, 'c': 3}, 'd': 3}
    
    result = comparator.compare(dict1, dict2)
    assert 'a.b' in result['identical']
    assert 'a.c' in result['different']
    assert 'd' in result['identical']

def test_compare_lists():
    comparator = ResultComparator()
    list1 = [1, 2, 3]
    list2 = [1, 4, 3]
    
    result = comparator.compare({'items': list1}, {'items': list2})
    assert 'items.0' in result['identical']
    assert 'items.1' in result['different']
    assert 'items.2' in result['identical']

def test_compare_nested_lists():
    comparator = ResultComparator()
    dict1 = {'items': [{'id': 1, 'value': 'a'}, {'id': 2, 'value': 'b'}]}
    dict2 = {'items': [{'id': 1, 'value': 'a'}, {'id': 2, 'value': 'c'}]}
    
    result = comparator.compare(dict1, dict2)
    assert 'items.0.id' in result['identical']
    assert 'items.0.value' in result['identical']
    assert 'items.1.id' in result['identical']
    assert 'items.1.value' in result['different']

def test_compare_missing_keys():
    comparator = ResultComparator()
    dict1 = {'a': 1, 'b': 2}
    dict2 = {'a': 1}
    
    result = comparator.compare(dict1, dict2)
    assert 'a' in result['identical']
    assert 'b' in result['missing']

def test_compare_extra_keys():
    comparator = ResultComparator()
    dict1 = {'a': 1}
    dict2 = {'a': 1, 'b': 2}
    
    result = comparator.compare(dict1, dict2)
    assert 'a' in result['identical']
    assert 'b' in result['extra']

def test_get_summary():
    comparator = ResultComparator()
    dict1 = {'a': 1, 'b': 2, 'c': {'d': 3}}
    dict2 = {'a': 1, 'b': 3, 'c': {'d': 4}}
    
    result = comparator.compare(dict1, dict2)
    summary = comparator.get_summary(result)
    
    assert 'identical: 1 differences' in summary
    assert 'different: 2 differences' in summary
    assert '  - b' in summary
    assert '  - c.d' in summary 
from typing import Dict, Any, List, Union
from .parallel_config import AgentVersion
import json

class ResultComparator:
    """Compare results from parallel implementations"""
    
    def __init__(self):
        self.comparison_keys = {
            'identical': 'identical',
            'different': 'different',
            'missing': 'missing',
            'extra': 'extra'
        }
    
    def compare(self, result1: Dict[str, Any], result2: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two results and return a comparison dictionary"""
        comparison = {
            self.comparison_keys['identical']: [],
            self.comparison_keys['different']: [],
            self.comparison_keys['missing']: [],
            self.comparison_keys['extra']: []
        }
        
        self._compare_dicts(result1, result2, comparison, [])
        return comparison
    
    def _compare_dicts(self, dict1: Dict[str, Any], dict2: Dict[str, Any], 
                      comparison: Dict[str, List[str]], path: List[str]) -> None:
        """Recursively compare two dictionaries"""
        # Check keys in dict1
        for key in dict1:
            current_path = path + [key]
            path_str = '.'.join(current_path)
            
            if key not in dict2:
                comparison[self.comparison_keys['missing']].append(path_str)
                continue
            
            value1 = dict1[key]
            value2 = dict2[key]
            
            if isinstance(value1, dict) and isinstance(value2, dict):
                self._compare_dicts(value1, value2, comparison, current_path)
            elif isinstance(value1, list) and isinstance(value2, list):
                self._compare_lists(value1, value2, comparison, current_path)
            elif value1 == value2:
                comparison[self.comparison_keys['identical']].append(path_str)
            else:
                comparison[self.comparison_keys['different']].append(path_str)
        
        # Check for extra keys in dict2
        for key in dict2:
            if key not in dict1:
                path_str = '.'.join(path + [key])
                comparison[self.comparison_keys['extra']].append(path_str)
    
    def _compare_lists(self, list1: List[Any], list2: List[Any], 
                      comparison: Dict[str, List[str]], path: List[str]) -> None:
        """Compare two lists"""
        path_str = '.'.join(path)
        
        if len(list1) != len(list2):
            comparison[self.comparison_keys['different']].append(f"{path_str}.length")
            return
        
        for i, (item1, item2) in enumerate(zip(list1, list2)):
            current_path = path + [str(i)]
            
            if isinstance(item1, dict) and isinstance(item2, dict):
                self._compare_dicts(item1, item2, comparison, current_path)
            elif isinstance(item1, list) and isinstance(item2, list):
                self._compare_lists(item1, item2, comparison, current_path)
            elif item1 == item2:
                comparison[self.comparison_keys['identical']].append('.'.join(current_path))
            else:
                comparison[self.comparison_keys['different']].append('.'.join(current_path))
    
    def get_summary(self, comparison: Dict[str, List[str]]) -> str:
        """Get a human-readable summary of the comparison"""
        summary = []
        for key, paths in comparison.items():
            if paths:
                summary.append(f"{key}: {len(paths)} differences")
                for path in paths:
                    summary.append(f"  - {path}")
        return '\n'.join(summary) 
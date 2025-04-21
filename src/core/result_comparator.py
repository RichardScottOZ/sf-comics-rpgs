from typing import Dict, Any, List
from .parallel_config import AgentVersion

class ResultComparator:
    """Compare results from parallel implementations"""
    
    def compare_results(self, original: Dict[str, Any], mcp: Dict[str, Any]) -> Dict[str, Any]:
        """Compare results from both implementations"""
        comparison = {
            'matches': True,
            'differences': [],
            'original_count': len(original.get('items', [])),
            'mcp_count': len(mcp.get('items', [])),
            'common_items': [],
            'unique_to_original': [],
            'unique_to_mcp': [],
            'performance': {
                'original_time': original.get('execution_time', 0),
                'mcp_time': mcp.get('execution_time', 0)
            }
        }
        
        # Handle error cases
        if 'error' in original:
            comparison['original_error'] = original['error']
            comparison['matches'] = False
        if 'error' in mcp:
            comparison['mcp_error'] = mcp['error']
            comparison['matches'] = False
            
        if 'error' in original or 'error' in mcp:
            return comparison
            
        # Compare item lists
        original_items = {item['id']: item for item in original.get('items', [])}
        mcp_items = {item['id']: item for item in mcp.get('items', [])}
        
        # Find common and unique items
        common_ids = set(original_items.keys()) & set(mcp_items.keys())
        comparison['common_items'] = list(common_ids)
        
        comparison['unique_to_original'] = list(
            set(original_items.keys()) - set(mcp_items.keys())
        )
        comparison['unique_to_mcp'] = list(
            set(mcp_items.keys()) - set(original_items.keys())
        )
        
        # Check for differences in common items
        for item_id in common_ids:
            if original_items[item_id] != mcp_items[item_id]:
                comparison['matches'] = False
                comparison['differences'].append({
                    'id': item_id,
                    'original': original_items[item_id],
                    'mcp': mcp_items[item_id]
                })
                
        return comparison
    
    def get_summary(self, comparison: Dict[str, Any]) -> str:
        """Get human-readable summary of comparison"""
        summary = []
        
        if 'original_error' in comparison:
            summary.append("Original implementation failed: " + comparison['original_error'])
        if 'mcp_error' in comparison:
            summary.append("MCP implementation failed: " + comparison['mcp_error'])
            
        if 'original_error' in comparison or 'mcp_error' in comparison:
            return "\n".join(summary)
            
        summary.extend([
            f"Original results: {comparison['original_count']} items",
            f"MCP results: {comparison['mcp_count']} items",
            f"Common items: {len(comparison['common_items'])}",
            f"Unique to original: {len(comparison['unique_to_original'])}",
            f"Unique to MCP: {len(comparison['unique_to_mcp'])}"
        ])
        
        if not comparison['matches']:
            summary.append(f"Found {len(comparison['differences'])} differences in common items")
            
        performance = comparison['performance']
        summary.extend([
            f"Original execution time: {performance['original_time']:.2f}s",
            f"MCP execution time: {performance['mcp_time']:.2f}s"
        ])
        
        return "\n".join(summary) 
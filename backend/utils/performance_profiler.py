"""
Performance Profiler for API Endpoints

This module provides tools to measure and analyze API endpoint performance,
identifying bottlenecks and collecting baseline metrics.
"""

import time
import functools
import json
from datetime import datetime
from typing import Dict, List, Callable, Any, Optional
from collections import defaultdict
from flask import request, g
import statistics


class PerformanceMetrics:
    """Stores and analyzes performance metrics for API endpoints."""
    
    def __init__(self):
        self._metrics: Dict[str, List[float]] = defaultdict(list)
        self._request_counts: Dict[str, int] = defaultdict(int)
        self._slow_requests: List[Dict[str, Any]] = []
        self._start_time = datetime.now()
    
    def record_request(self, endpoint: str, method: str, duration: float, 
                      status_code: int, path: str):
        """Record a request's performance metrics."""
        key = f"{method} {endpoint}"
        self._metrics[key].append(duration)
        self._request_counts[key] += 1
        
        # Track slow requests (> 500ms as per requirement)
        if duration > 0.5:
            self._slow_requests.append({
                'endpoint': endpoint,
                'method': method,
                'path': path,
                'duration': duration,
                'status_code': status_code,
                'timestamp': datetime.now().isoformat()
            })
    
    def get_endpoint_stats(self, endpoint_key: str) -> Dict[str, Any]:
        """Get statistics for a specific endpoint."""
        if endpoint_key not in self._metrics or not self._metrics[endpoint_key]:
            return {}
        
        durations = self._metrics[endpoint_key]
        sorted_durations = sorted(durations)
        count = len(durations)
        
        return {
            'count': count,
            'min': min(durations),
            'max': max(durations),
            'mean': statistics.mean(durations),
            'median': statistics.median(durations),
            'p95': sorted_durations[int(count * 0.95)] if count > 0 else 0,
            'p99': sorted_durations[int(count * 0.99)] if count > 0 else 0,
            'total_time': sum(durations)
        }
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all endpoints."""
        stats = {}
        for endpoint_key in self._metrics:
            stats[endpoint_key] = self.get_endpoint_stats(endpoint_key)
        return stats
    
    def get_bottlenecks(self, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Identify bottlenecks - endpoints with p95 response time > threshold.
        
        Args:
            threshold: Response time threshold in seconds (default 0.5s per requirement)
        
        Returns:
            List of bottleneck endpoints with their statistics
        """
        bottlenecks = []
        for endpoint_key, stats in self.get_all_stats().items():
            if stats.get('p95', 0) > threshold:
                bottlenecks.append({
                    'endpoint': endpoint_key,
                    'p95': stats['p95'],
                    'mean': stats['mean'],
                    'max': stats['max'],
                    'count': stats['count']
                })
        
        # Sort by p95 descending
        bottlenecks.sort(key=lambda x: x['p95'], reverse=True)
        return bottlenecks
    
    def get_slow_requests(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get the slowest requests recorded."""
        sorted_requests = sorted(
            self._slow_requests, 
            key=lambda x: x['duration'], 
            reverse=True
        )
        return sorted_requests[:limit]
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive performance report."""
        all_stats = self.get_all_stats()
        bottlenecks = self.get_bottlenecks()
        
        # Calculate overall statistics
        all_durations = []
        for durations in self._metrics.values():
            all_durations.extend(durations)
        
        total_requests = sum(self._request_counts.values())
        
        overall_stats = {}
        if all_durations:
            sorted_all = sorted(all_durations)
            overall_stats = {
                'total_requests': total_requests,
                'total_endpoints': len(self._metrics),
                'mean_response_time': statistics.mean(all_durations),
                'median_response_time': statistics.median(all_durations),
                'p95_response_time': sorted_all[int(len(sorted_all) * 0.95)] if sorted_all else 0,
                'p99_response_time': sorted_all[int(len(sorted_all) * 0.99)] if sorted_all else 0,
                'min_response_time': min(all_durations),
                'max_response_time': max(all_durations),
                'slow_requests_count': len(self._slow_requests),
                'slow_requests_percentage': (len(self._slow_requests) / total_requests * 100) if total_requests > 0 else 0
            }
        
        return {
            'report_generated_at': datetime.now().isoformat(),
            'profiling_started_at': self._start_time.isoformat(),
            'overall_statistics': overall_stats,
            'endpoint_statistics': all_stats,
            'bottlenecks': bottlenecks,
            'slowest_requests': self.get_slow_requests(20)
        }
    
    def reset(self):
        """Reset all metrics."""
        self._metrics.clear()
        self._request_counts.clear()
        self._slow_requests.clear()
        self._start_time = datetime.now()


# Global metrics instance
_metrics = PerformanceMetrics()


def get_metrics() -> PerformanceMetrics:
    """Get the global metrics instance."""
    return _metrics


def profile_endpoint(func: Callable) -> Callable:
    """
    Decorator to profile individual endpoint functions.
    
    Usage:
        @app.route('/api/endpoint')
        @profile_endpoint
        def my_endpoint():
            return {'data': 'value'}
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            
            # Get endpoint info from request context
            endpoint = request.endpoint or 'unknown'
            method = request.method
            path = request.path
            
            # Get status code from response if available
            status_code = 200  # Default
            if hasattr(g, 'status_code'):
                status_code = g.status_code
            
            _metrics.record_request(endpoint, method, duration, status_code, path)
    
    return wrapper


def init_performance_profiler(app):
    """
    Initialize performance profiling middleware for Flask app.
    
    This middleware automatically profiles all requests without requiring
    decorators on individual endpoints.
    
    Args:
        app: Flask application instance
    """
    
    @app.before_request
    def before_request():
        """Record request start time."""
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        """Record request completion and metrics."""
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            endpoint = request.endpoint or 'unknown'
            method = request.method
            path = request.path
            status_code = response.status_code
            
            _metrics.record_request(endpoint, method, duration, status_code, path)
        
        return response
    
    # Add profiling routes
    @app.route('/api/admin/performance/stats')
    def performance_stats():
        """Get current performance statistics."""
        from flask import jsonify
        stats = _metrics.get_all_stats()
        return jsonify({
            'success': True,
            'data': stats
        })
    
    @app.route('/api/admin/performance/report')
    def performance_report():
        """Get comprehensive performance report."""
        from flask import jsonify
        report = _metrics.generate_report()
        return jsonify({
            'success': True,
            'data': report
        })
    
    @app.route('/api/admin/performance/bottlenecks')
    def performance_bottlenecks():
        """Get identified bottlenecks."""
        from flask import jsonify
        bottlenecks = _metrics.get_bottlenecks()
        return jsonify({
            'success': True,
            'data': bottlenecks
        })
    
    @app.route('/api/admin/performance/reset', methods=['POST'])
    def performance_reset():
        """Reset performance metrics."""
        from flask import jsonify
        _metrics.reset()
        return jsonify({
            'success': True,
            'message': 'Performance metrics reset successfully'
        })


def save_report_to_file(filename: str = 'performance_baseline.json'):
    """
    Save the current performance report to a file.
    
    Args:
        filename: Output filename for the report
    """
    report = _metrics.generate_report()
    
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    return filename

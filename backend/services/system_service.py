"""
System metrics service - Real system monitoring
Provides real-time system metrics using psutil
"""

import psutil
import time
import platform
from datetime import datetime, timedelta


class SystemMetrics:
    def __init__(self):
        self.boot_time = psutil.boot_time()
        
    def get_cpu_info(self):
        """Get CPU usage and information"""
        return {
            'percent': round(psutil.cpu_percent(interval=1), 1),
            'count': psutil.cpu_count(),
            'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
        }
    
    def get_memory_info(self):
        """Get memory usage information"""
        memory = psutil.virtual_memory()
        return {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': round(memory.percent, 1),
            'total_gb': round(memory.total / (1024**3), 1),
            'used_gb': round(memory.used / (1024**3), 1),
            'available_gb': round(memory.available / (1024**3), 1)
        }
    
    def get_disk_info(self):
        """Get disk usage information"""
        try:
            disk = psutil.disk_usage('/')
        except:
            # Windows fallback
            disk = psutil.disk_usage('C:')
            
        return {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': round((disk.used / disk.total) * 100, 1),
            'total_gb': round(disk.total / (1024**3), 1),
            'used_gb': round(disk.used / (1024**3), 1),
            'free_gb': round(disk.free / (1024**3), 1)
        }
    
    def get_network_info(self):
        """Get network statistics"""
        net_io = psutil.net_io_counters()
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'bytes_sent_mb': round(net_io.bytes_sent / (1024**2), 1),
            'bytes_recv_mb': round(net_io.bytes_recv / (1024**2), 1)
        }
    
    def get_uptime(self):
        """Get system uptime"""
        uptime_seconds = time.time() - self.boot_time
        uptime_delta = timedelta(seconds=uptime_seconds)
        
        days = uptime_delta.days
        hours, remainder = divmod(uptime_delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            uptime_str = f"{days}j {hours}h {minutes}m"
        elif hours > 0:
            uptime_str = f"{hours}h {minutes}m"
        else:
            uptime_str = f"{minutes}m"
            
        return {
            'seconds': uptime_seconds,
            'formatted': uptime_str,
            'boot_time': datetime.fromtimestamp(self.boot_time).strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_processes_info(self):
        """Get running processes information"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        
        return {
            'total_count': len(processes),
            'top_processes': processes[:10]  # Top 10 CPU consumers
        }
    
    def get_system_info(self):
        """Get general system information"""
        return {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'hostname': platform.node(),
            'processor': platform.processor()
        }
    
    def get_all_metrics(self):
        """Get all system metrics in one call"""
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'disk': self.get_disk_info(),
            'network': self.get_network_info(),
            'uptime': self.get_uptime(),
            'processes': self.get_processes_info(),
            'system': self.get_system_info()
        }
    
    def _availability_score(self, cpu_pct: float, memory_pct: float, disk_pct: float) -> float:
        """Score 0–100 for dashboard display (higher is better)."""
        score = 100.0
        score -= max(0.0, cpu_pct - 60) * 0.35
        score -= max(0.0, memory_pct - 70) * 0.4
        score -= max(0.0, disk_pct - 75) * 0.25
        return round(max(0.0, min(100.0, score)), 1)

    def get_health_status(self):
        """Get overall system health status"""
        cpu = self.get_cpu_info()
        memory = self.get_memory_info()
        disk = self.get_disk_info()

        status = "healthy"
        issues = []

        if cpu["percent"] >= 90:
            status = "critical"
            issues.append(f"CPU élevé : {cpu['percent']}%")
        elif cpu["percent"] >= 75:
            status = "warning"
            issues.append(f"CPU modéré : {cpu['percent']}%")

        if memory["percent"] >= 95:
            status = "critical"
            issues.append(f"Mémoire critique : {memory['percent']}%")
        elif memory["percent"] >= 88:
            if status != "critical":
                status = "warning"
            issues.append(f"Mémoire élevée : {memory['percent']}%")

        if disk["percent"] >= 95:
            status = "critical"
            issues.append(f"Disque critique : {disk['percent']}%")
        elif disk["percent"] >= 85:
            if status == "healthy":
                status = "warning"
            issues.append(f"Disque élevé : {disk['percent']}%")

        return {
            "status": status,
            "issues": issues,
            "availability_percent": self._availability_score(
                cpu["percent"], memory["percent"], disk["percent"]
            ),
        }

    def get_app_metrics(self) -> dict:
        """Métriques applicatives (réponses API, erreurs récentes)."""
        from datetime import timedelta

        from backend.models.audit_log import AuditLog
        from backend.utils.performance_profiler import get_metrics

        since = datetime.now() - timedelta(hours=24)
        errors_24h = AuditLog.query.filter(
            AuditLog.created_at >= since,
            AuditLog.action.ilike("%fail%"),
        ).count()

        profiler = get_metrics()
        report = profiler.generate_report()
        overall = report.get("overall_statistics") or {}

        total_requests = overall.get("total_requests", 0)
        elapsed_min = max(
            1.0,
            (datetime.now() - profiler._start_time).total_seconds() / 60,
        )
        requests_per_min = round(total_requests / elapsed_min, 1)

        mean_s = overall.get("mean_response_time")
        avg_response_ms = round(mean_s * 1000) if mean_s is not None else None

        return {
            "errors_24h": errors_24h,
            "requests_per_minute": requests_per_min,
            "avg_response_ms": avg_response_ms,
            "total_api_requests": total_requests,
        }


# Global instance
system_metrics = SystemMetrics()


def get_dashboard_metrics():
    """Get metrics formatted for dashboard display"""
    metrics = system_metrics.get_all_metrics()
    health = system_metrics.get_health_status()
    app_metrics = system_metrics.get_app_metrics()

    return {
        "cpu_percent": metrics["cpu"]["percent"],
        "memory_used_gb": metrics["memory"]["used_gb"],
        "memory_total_gb": metrics["memory"]["total_gb"],
        "memory_percent": metrics["memory"]["percent"],
        "disk_free_gb": metrics["disk"]["free_gb"],
        "disk_total_gb": metrics["disk"]["total_gb"],
        "disk_percent": metrics["disk"]["percent"],
        "uptime_formatted": metrics["uptime"]["formatted"],
        "availability_percent": health["availability_percent"],
        "process_count": metrics["processes"]["total_count"],
        "network_sent_mb": metrics["network"]["bytes_sent_mb"],
        "network_recv_mb": metrics["network"]["bytes_recv_mb"],
        "health_status": health["status"],
        "health_issues": health["issues"],
        "boot_time": metrics["uptime"]["boot_time"],
        "hostname": metrics["system"]["hostname"],
        "platform": f"{metrics['system']['platform']} {metrics['system']['platform_release']}",
        **app_metrics,
    }
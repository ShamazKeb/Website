import urllib.request
import urllib.parse
import json
from typing import Optional, Dict, Any


class PiholeManager:
    """
    Manager class for Pi-hole API communication.
    Controls Pi-hole status and retrieves statistics.
    Uses urllib (stdlib) to avoid conflicts with plugp100.requests.
    """
    
    def __init__(self, host: str = "localhost", port: int = 8080, api_token: str = ""):
        """
        Initialize PiholeManager.
        
        Args:
            host: Pi-hole server hostname/IP
            port: Web interface port (default 8080)
            api_token: API token from Pi-hole settings
        """
        self.base_url = f"http://{host}:{port}/admin/api.php"
        self.api_token = api_token
        self.enabled = True
        self.stats = {
            "queries_today": 0,
            "blocked_today": 0,
            "percent_blocked": 0.0
        }
    
    def _request(self, params: Dict[str, Any]) -> Optional[Dict]:
        """Make API request to Pi-hole using urllib."""
        try:
            if self.api_token:
                params["auth"] = self.api_token
            
            query_string = urllib.parse.urlencode(params)
            url = f"{self.base_url}?{query_string}"
            
            req = urllib.request.Request(url, method='GET')
            req.add_header('User-Agent', 'PiholeManager/1.0')
            
            with urllib.request.urlopen(req, timeout=5) as response:
                data = response.read().decode('utf-8')
                return json.loads(data)
        except Exception as e:
            print(f"[PiholeManager] Request failed: {e}")
            return None
    
    def get_status(self) -> bool:
        """
        Get current Pi-hole status.
        
        Returns:
            True if enabled, False if disabled
        """
        data = self._request({"status": ""})
        if data and "status" in data:
            self.enabled = data["status"] == "enabled"
            return self.enabled
        return self.enabled
    
    def enable(self) -> bool:
        """
        Enable Pi-hole blocking.
        
        Returns:
            True if successful
        """
        data = self._request({"enable": ""})
        if data and data.get("status") == "enabled":
            self.enabled = True
            return True
        return False
    
    def disable(self, seconds: int = 0) -> bool:
        """
        Disable Pi-hole blocking.
        
        Args:
            seconds: Duration in seconds (0 = indefinitely)
            
        Returns:
            True if successful
        """
        params = {"disable": str(seconds) if seconds > 0 else ""}
        data = self._request(params)
        if data and data.get("status") == "disabled":
            self.enabled = False
            return True
        return False
    
    def toggle(self) -> bool:
        """
        Toggle Pi-hole status.
        
        Returns:
            New status (True = enabled)
        """
        self.get_status()
        if self.enabled:
            self.disable()
        else:
            self.enable()
        return self.enabled
    
    def update_stats(self) -> Dict[str, Any]:
        """
        Fetch current statistics from Pi-hole.
        
        Returns:
            Dictionary with stats
        """
        data = self._request({"summaryRaw": ""})
        if data:
            self.stats = {
                "queries_today": int(data.get("dns_queries_today", 0)),
                "blocked_today": int(data.get("ads_blocked_today", 0)),
                "percent_blocked": float(data.get("ads_percentage_today", 0.0))
            }
            # Also update enabled status
            self.enabled = data.get("status") == "enabled"
        return self.stats
    
    def get_stats(self) -> Dict[str, Any]:
        """Return cached stats."""
        return self.stats

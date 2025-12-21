import urllib.request
import urllib.parse
import json
from typing import Optional, Dict, Any


class PiholeManager:
    """
    Manager class for Pi-hole v6 API communication.
    Controls Pi-hole status and retrieves statistics.
    """
    
    def __init__(self, host: str = "localhost", port: int = 8080, password: str = ""):
        """
        Initialize PiholeManager.
        
        Args:
            host: Pi-hole server hostname/IP
            port: Web interface port (default 8080)
            password: Pi-hole web interface password
        """
        self.base_url = f"http://{host}:{port}/api"
        self.password = password
        self.session_id = ""
        self.enabled = True
        self.stats = {
            "queries_today": 0,
            "blocked_today": 0,
            "percent_blocked": 0.0
        }
    
    def _request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Optional[Dict]:
        """Make API request to Pi-hole v6."""
        try:
            url = f"{self.base_url}/{endpoint}"
            
            # Add session ID if we have one
            headers = {'User-Agent': 'PiholeManager/1.0'}
            if self.session_id:
                headers['X-FTL-SID'] = self.session_id
            
            if method == "POST" and data:
                json_data = json.dumps(data).encode('utf-8')
                req = urllib.request.Request(url, data=json_data, method='POST')
                req.add_header('Content-Type', 'application/json')
            else:
                req = urllib.request.Request(url, method=method)
            
            for key, value in headers.items():
                req.add_header(key, value)
            
            with urllib.request.urlopen(req, timeout=5) as response:
                result = response.read().decode('utf-8')
                return json.loads(result) if result else {}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else ""
            print(f"[PiholeManager] HTTP {e.code}: {error_body}")
            return None
        except Exception as e:
            print(f"[PiholeManager] Request failed: {e}")
            return None
    
    def login(self) -> bool:
        """Authenticate with Pi-hole and get session ID."""
        if not self.password:
            print("[PiholeManager] No password configured")
            return False
        
        data = {"password": self.password}
        result = self._request("auth", method="POST", data=data)
        
        if result and "session" in result:
            self.session_id = result["session"].get("sid", "")
            print(f"[PiholeManager] Logged in successfully")
            return True
        return False
    
    def get_status(self) -> bool:
        """Get current Pi-hole blocking status."""
        # Try to login if we don't have a session
        if not self.session_id:
            self.login()
        
        result = self._request("dns/blocking")
        if result and "blocking" in result:
            # API returns string "enabled"/"disabled", convert to bool
            self.enabled = result["blocking"] == "enabled"
            return self.enabled
        return self.enabled
    
    def enable(self) -> bool:
        """Enable Pi-hole blocking."""
        if not self.session_id:
            self.login()
        
        result = self._request("dns/blocking", method="POST", data={"blocking": True})
        if result and result.get("blocking") == "enabled":
            self.enabled = True
            print("[PiholeManager] Blocking enabled")
            return True
        print(f"[PiholeManager] Enable failed: {result}")
        return False
    
    def disable(self, seconds: int = 0) -> bool:
        """Disable Pi-hole blocking."""
        if not self.session_id:
            self.login()
        
        data = {"blocking": False}
        if seconds > 0:
            data["timer"] = seconds
        
        result = self._request("dns/blocking", method="POST", data=data)
        if result and result.get("blocking") == "disabled":
            self.enabled = False
            print("[PiholeManager] Blocking disabled")
            return True
        print(f"[PiholeManager] Disable failed: {result}")
        return False
    
    def toggle(self) -> bool:
        """Toggle Pi-hole status."""
        self.get_status()
        if self.enabled:
            self.disable()
        else:
            self.enable()
        return self.enabled
    
    def update_stats(self) -> Dict[str, Any]:
        """Fetch current statistics from Pi-hole."""
        if not self.session_id:
            self.login()
        
        result = self._request("stats/summary")
        if result:
            self.stats = {
                "queries_today": int(result.get("queries", {}).get("total", 0)),
                "blocked_today": int(result.get("queries", {}).get("blocked", 0)),
                "percent_blocked": float(result.get("queries", {}).get("percent_blocked", 0.0))
            }
            self.enabled = result.get("gravity", {}).get("blocking", True)
        return self.stats
    
    def get_stats(self) -> Dict[str, Any]:
        """Return cached stats."""
        return self.stats

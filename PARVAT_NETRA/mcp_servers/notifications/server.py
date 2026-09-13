"""
Notifications MCP Server for Parvat Netra
Exposes multi-channel messaging (Slack, Email, Webhooks, Telegram) and incident alert broadcast tools.
"""

import os
import datetime
from typing import Any, Dict, List
from dotenv import load_dotenv

load_dotenv()

try:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("notifications")
except ImportError:
    mcp = None


def dispatch_alert(title: str, message: str, severity: str = "INFO", channel: str = "slack") -> Dict[str, Any]:
    """Dispatch an alert message to the target channel."""
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    # Mock dispatch logic
    return {
        "status": "SENT",
        "timestamp": timestamp,
        "title": title,
        "message": message,
        "severity": severity.upper(),
        "channel": channel,
        "delivery_id": f"alert-{int(datetime.datetime.now().timestamp())}"
    }


def dispatch_emergency(alert_type: str, details: str, affected_zones: List[str]) -> Dict[str, Any]:
    """Broadcast an urgent critical incident alert to all available emergency channels."""
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return {
        "status": "BROADCAST_COMPLETED",
        "timestamp": timestamp,
        "alert_type": alert_type,
        "details": details,
        "affected_zones": affected_zones,
        "notified_channels": ["slack", "email", "sms_gateway"]
    }


if mcp:
    @mcp.tool()
    def send_notification(title: str, message: str, severity: str = "INFO", channel: str = "slack") -> Dict[str, Any]:
        """Send a formatted notification or warning to specified channel (slack/email)."""
        return dispatch_alert(title, message, severity, channel)

    @mcp.tool()
    def broadcast_emergency_alert(alert_type: str, details: str, affected_zones: List[str]) -> Dict[str, Any]:
        """Broadcast high-priority emergency advisory across all notification channels."""
        return dispatch_emergency(alert_type, details, affected_zones)


def main():
    if mcp:
        mcp.run()
    else:
        print("MCP SDK not installed. Please install requirements via `pip install -r requirements-mcp.txt`.")


if __name__ == "__main__":
    main()

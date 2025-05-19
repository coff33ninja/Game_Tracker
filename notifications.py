# notifications.py
import sqlite3
from plyer import notification
from db_manager import DBManager
from datetime import datetime, timedelta, timezone # Added datetime, timedelta, timezone


class Notifications:
    def __init__(self, db_manager: DBManager, email_config=None):
        self.db = db_manager
        # email_config is no longer used

    def send_desktop_notification(self, title, message):
        # Windows notification message limit for szTip is 256 WCHARs.
        # Truncate if longer to prevent ValueError, leaving space for ellipsis.
        max_len = 250  # Be a bit conservative
        if len(message) > max_len:
            message = message[:max_len] + "..."

        # Safely get the notify method and check if it's callable
        notify_method = getattr(notification, 'notify', None)
        if callable(notify_method):
            try:
                notify_method(
                    title=title, message=message, app_name="Free Games Arcade", timeout=10
                )
            except Exception as e:
                # Catching generic Exception as plyer backends can raise various errors
                print(f"Desktop notification failed: {e}")
        else:
            print("Desktop notification method (plyer.notification.notify) is not available or not callable.")

    def notify_new_games(self):
        games = self.db.get_games_by_status("active")
        if games:
            message = "\n".join(f"{g[1]} on {g[0]}: {g[2]}" for g in games)
            self.send_desktop_notification("New Free Games", message)

    def notify_expiring_games(self):
        conn = sqlite3.connect(self.db.db_path)
        # It's generally better to have DBManager handle all DB interactions,
        # but for this fix, we'll adjust the existing direct access.
        cursor = conn.cursor()
        now_utc = datetime.now(timezone.utc)
        one_day_from_now_utc = now_utc + timedelta(days=1)

        cursor.execute(
            "SELECT platform, title, end_date FROM games WHERE status = 'active' AND end_date IS NOT NULL"
        )
        expiring_games_details = []
        for p_platform, t_title, e_end_date_str in cursor.fetchall():
            try:
                game_end_date_obj = datetime.fromisoformat(e_end_date_str)
                if game_end_date_obj.tzinfo is None or game_end_date_obj.tzinfo.utcoffset(game_end_date_obj) is None:
                    game_end_date_obj = game_end_date_obj.replace(tzinfo=timezone.utc)

                if game_end_date_obj < one_day_from_now_utc: # Compare aware datetimes
                    expiring_games_details.append((p_platform, t_title, e_end_date_str)) # Keep original string for message
            except ValueError:
                print(f"Warning: Could not parse end_date string '{e_end_date_str}' for game '{t_title}'. Skipping expiring notification for this game.")
        conn.close()
        if expiring_games_details:
            message = "\n".join(f"{t} on {p} expires soon: {e}" for p, t, e in expiring_games_details)
            self.send_desktop_notification("Expiring Free Games", message)

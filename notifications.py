# notifications.py
from plyer import notification
import smtplib
from email.mime.text import MIMEText
from db_manager import DBManager
from datetime import datetime, timedelta, timezone # Added datetime, timedelta, timezone


class Notifications:
    def __init__(self, db_manager: DBManager, email_config=None):
        self.db = db_manager
        self.email_config = (
            email_config  # {"smtp_server", "port", "sender", "password", "receiver"}
        )

    def send_desktop_notification(self, title, message):
        notification.notify(
            title=title, message=message, app_name="Free Games Arcade", timeout=10
        )

    def send_email_notification(self, subject, body):
        if not self.email_config:
            return
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.email_config["sender"]
        msg["To"] = self.email_config["receiver"]
        with smtplib.SMTP_SSL(
            self.email_config["smtp_server"], self.email_config["port"]
        ) as server:
            server.login(self.email_config["sender"], self.email_config["password"])
            server.send_message(msg)

    def notify_new_games(self):
        games = self.db.get_games_by_status("active")
        if games:
            message = "\n".join(f"{g[1]} on {g[0]}: {g[2]}" for g in games)
            self.send_desktop_notification("New Free Games", message)
            self.send_email_notification("New Free Games Available", message)

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
            self.send_email_notification("Free Games Expiring Soon", message)

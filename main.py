# main.py
from ttkbootstrap import Window
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from db_manager import DBManager
from scraper import GameScraper
from owned_games import OwnedGames
from ai_module import AIModule
from gui import FreeGamesGUI
from library_import import LibraryImport
from price_tracker import PriceTracker
from notifications import Notifications
from game_filter import GameFilter
from ai_recommendations import AIRecommendations
from export_backup import ExportBackup
from cloud_sync import CloudSync
from genre_tagging import GenreTagging
from multi_language import MultiLanguage
from analytics import Analytics
import asyncio


def schedule_scraping(scraper, gui, multi_language):
    # The new _execute_full_refresh_cycle in gui handles all scraping and processing
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        lambda: asyncio.run(gui._execute_full_refresh_cycle()), "cron", day_of_week="mon-sun", hour=8
    )
    scheduler.add_job(
        lambda: asyncio.run(gui._execute_full_refresh_cycle()),
        "cron",
        day_of_week="tue,thu",
        hour=11,
    )
    scheduler.start()


if __name__ == "__main__":
    db = DBManager()
    ai = AIModule()
    scraper = GameScraper(ai_module=ai)
    owned_games = OwnedGames(db)
    game_filter = GameFilter(db)
    notifications = Notifications(db) # Email config removed
    library_import = LibraryImport(db)
    price_tracker = PriceTracker(db)
    ai_recommendations = AIRecommendations(ai, db)
    export_backup = ExportBackup(db)
    genre_tagging = GenreTagging(ai, db)
    multi_language = MultiLanguage(ai, db)
    analytics = Analytics(db)

    # --- Cloud Sync Configuration ---
    ENABLE_CLOUD_SYNC = False  # Set this to True to enable, False to bypass
    cloud_sync = None

    if ENABLE_CLOUD_SYNC:
        try:
            cloud_sync_aws_config = {
                "aws_access_key_id": "your_key",  # Consider using environment variables
                "aws_secret_access_key": "your_secret",
                "bucket": "your_bucket",
            }
            cloud_sync = CloudSync(db, aws_config=cloud_sync_aws_config)
            print("CloudSync initialized.")
        except Exception as e:
            print(f"Failed to initialize CloudSync: {e}. Proceeding without cloud sync.")
            cloud_sync = None # Ensure it's None on failure
    else:
        print("CloudSync is disabled by configuration. Proceeding without cloud sync.")

    root = Window()
    gui = FreeGamesGUI(
        root,
        db,
        owned_games,
        game_filter,
        notifications,
        library_import,
        price_tracker,
        ai_recommendations,
        export_backup,
        cloud_sync,
        genre_tagging,
        multi_language,
        analytics,
        scraper, # Pass the scraper instance to the GUI
    )
    scheduler_thread = threading.Thread(
        target=schedule_scraping, args=(scraper, gui, multi_language), daemon=True
    )
    scheduler_thread.start()
    root.mainloop()

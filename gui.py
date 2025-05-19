# gui.py
import tkinter as tk
from tkinter import simpledialog, messagebox # Added simpledialog and messagebox
from ttkbootstrap import Style, Notebook, Button, Label, Entry, Frame # Removed Window
import ttkbootstrap as ttk
import sqlite3
import asyncio
import threading
import webbrowser
from PIL import Image, ImageTk
from db_manager import DBManager
from owned_games import OwnedGames
from game_filter import GameFilter
from notifications import Notifications
from library_import import LibraryImport
from price_tracker import PriceTracker
from ai_recommendations import AIRecommendations
from export_backup import ExportBackup
from cloud_sync import CloudSync
from genre_tagging import GenreTagging
from multi_language import MultiLanguage
from analytics import Analytics
from scraper import FreeGame # For type hinting


class FreeGamesGUI:
    def __init__(
        self,
        root,
        db_manager: DBManager,
        owned_games: OwnedGames,
        game_filter: GameFilter,
        notifications: Notifications,
        library_import: LibraryImport,
        price_tracker: PriceTracker,
        ai_recommendations: AIRecommendations,
        export_backup: ExportBackup,
        cloud_sync: CloudSync,
        genre_tagging: GenreTagging,
        multi_language: MultiLanguage,
        analytics: Analytics,
        scraper, # Add scraper instance
    ):
        self.root = root
        self.db = db_manager
        self.owned_games = owned_games
        self.game_filter = game_filter
        self.notifications = notifications
        self.library_import = library_import
        self.price_tracker = price_tracker
        self.ai_recommendations = ai_recommendations
        self.export_backup = export_backup
        self.cloud_sync = cloud_sync
        self.genre_tagging = genre_tagging
        self.multi_language = multi_language
        self.analytics = analytics
        self.scraper = scraper # Store scraper instance
        self.root.title("Free Games Arcade")
        Style("cyborg")
        self.root.geometry("1000x700")

        # Load gamepad icon
        try:
            img = Image.open("gamepad.png").resize((20, 20))
            self.gamepad_icon = ImageTk.PhotoImage(img)
        except Exception: # Catch generic exception for file not found, PIL not installed, etc.
            # Create a 1x1 transparent PhotoImage as a fallback
            self.gamepad_icon = ImageTk.PhotoImage(Image.new('RGBA', (1, 1), (0,0,0,0)))

        # Main frame
        self.main_frame = Frame(root)
        self.main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Header
        Label(
            self.main_frame,
            text="Free Games Arcade",
            font=("Orbitron", 24, "bold"),
            foreground="#00FFFF",
        ).pack(pady=10)

        # Tabs
        self.notebook = Notebook(self.main_frame, bootstyle="primary") # type: ignore
        self.active_tab = tk.Frame(self.notebook)
        self.claimed_tab = tk.Frame(self.notebook)
        self.expired_tab = tk.Frame(self.notebook)
        self.owned_tab = tk.Frame(self.notebook)
        self.recommend_tab = tk.Frame(self.notebook)
        self.stats_tab = tk.Frame(self.notebook)
        self.notebook.add(self.active_tab, text="Active Free Games")
        self.notebook.add(self.claimed_tab, text="Claimed Games")
        self.notebook.add(self.expired_tab, text="Game Graveyard")
        self.notebook.add(self.owned_tab, text="Trophy Case")
        self.notebook.add(self.recommend_tab, text="Recommendations")
        self.notebook.add(self.stats_tab, text="Stats")
        self.notebook.pack(expand=True, fill="both")

        # Active Games Table
        self.active_headers = [
            "Platform",
            "Title",
            "Claim",
            "Mark Owned",
            "End Date",
            "Price",
            "Genre",
        ]
        self.active_labels = [
            Label(
                self.active_tab,
                text=h,
                font=("Press Start 2P", 10),
                foreground="#FF69B4",
            )
            for h in self.active_headers
        ]
        for i, label in enumerate(self.active_labels):
            label.grid(row=0, column=i, padx=5, pady=5, sticky="w")
        self.active_filter_frame = Frame(self.active_tab)
        self.active_filter_frame.grid(row=1, column=0, columnspan=7, pady=5)
        Label(self.active_filter_frame, text="Search:", foreground="#FFFFFF").grid(
            row=0, column=0
        )
        self.active_search = Entry(self.active_filter_frame, bootstyle="info")  # type: ignore
        self.active_search.grid(row=0, column=1, padx=5)
        Label(self.active_filter_frame, text="Platform:", foreground="#FFFFFF").grid(
            row=0, column=2
        )
        self.active_platform = ttk.Combobox(
            self.active_filter_frame,
            values=["All", "Epic", "Amazon Prime", "GOG", "Steam", "Ubisoft"],
            bootstyle="info", # type: ignore
        )
        self.active_platform.grid(row=0, column=3, padx=5)
        self.active_platform.set("All")
        Label(self.active_filter_frame, text="Genre:", foreground="#FFFFFF").grid(
            row=0, column=4
        )
        self.active_genre = ttk.Combobox(
            self.active_filter_frame,
            values=["All", "RPG", "FPS", "Adventure", "Strategy"],
            bootstyle="info",  # type: ignore
        )
        self.active_genre.grid(row=0, column=5, padx=5)
        self.active_genre.set("All")
        Button(
            self.active_filter_frame,
            text="Filter",
            command=self.update_active_gui,
            bootstyle="info-outline",  # type: ignore
        ).grid(row=0, column=6, padx=5)

        # Claimed Games Table
        self.claimed_headers = ["Platform", "Title", "Claim Date", "Price", "Genre"]
        self.claimed_labels = [
            Label(
                self.claimed_tab,
                text=h,
                font=("Press Start 2P", 10),
                foreground="#00FF00",
            )
            for h in self.claimed_headers
        ]
        for i, label in enumerate(self.claimed_labels):
            label.grid(row=0, column=i, padx=5, pady=5, sticky="w")
        Label(
            self.claimed_tab,
            text="Mission Complete",
            font=("Orbitron", 14),
            foreground="#00FF00",
        ).grid(row=1, column=0, columnspan=5, pady=5)

        # Expired Games Table
        self.expired_headers = ["Platform", "Title", "Epitaph", "Price", "Genre"]
        self.expired_labels = [
            Label(
                self.expired_tab,
                text=h,
                font=("Press Start 2P", 10),
                foreground="#FF4500",
            )
            for h in self.expired_headers
        ]
        for i, label in enumerate(self.expired_labels):
            label.grid(row=0, column=i, padx=5, pady=5, sticky="w")
        Label(
            self.expired_tab,
            text="Missed Opportunities",
            font=("Orbitron", 14),
            foreground="#FF4500",
        ).grid(row=1, column=0, columnspan=5, pady=5)

        # Owned Games Table
        self.owned_headers = ["Platform", "Title", "Acquisition Date", "Price", "Genre"]
        self.owned_labels = [
            Label(
                self.owned_tab,
                text=h,
                font=("Press Start 2P", 10),
                foreground="#FFD700",
            )
            for h in self.owned_headers
        ]
        for i, label in enumerate(self.owned_labels):
            label.grid(row=0, column=i, padx=5, pady=5, sticky="w")
        Label(
            self.owned_tab,
            text="Your Epic Collection",
            font=("Orbitron", 14),
            foreground="#FFD700",
        ).grid(row=1, column=0, columnspan=5, pady=5)
        self.owned_form_frame = Frame(self.owned_tab, bootstyle="dark")  # type: ignore
        self.owned_form_frame.grid(row=2, column=0, columnspan=5, pady=10)
        Label(
            self.owned_form_frame,
            text="Add to Trophy Case",
            font=("Orbitron", 12),
            foreground="#00FFFF",
        ).grid(row=0, column=0, columnspan=2)
        Label(self.owned_form_frame, text="Title:", foreground="#FFFFFF").grid(
            row=1, column=0, sticky="e"
        )
        self.title_entry = Entry(self.owned_form_frame, bootstyle="info")  # type: ignore
        self.title_entry.grid(row=1, column=1, padx=5)
        Label(self.owned_form_frame, text="Platform:", foreground="#FFFFFF").grid(
            row=2, column=0, sticky="e"
        )
        self.platform_entry = ttk.Combobox(
            self.owned_form_frame,
            values=["Epic", "Amazon Prime", "GOG", "Steam", "Ubisoft"],
            bootstyle="info",  # type: ignore
        )
        self.platform_entry.grid(row=2, column=1, padx=5)
        Label(self.owned_form_frame, text="URL (optional):", foreground="#FFFFFF").grid(
            row=3, column=0, sticky="e"
        )
        self.url_entry = Entry(self.owned_form_frame, bootstyle="info")  # type: ignore
        self.url_entry.grid(row=3, column=1, padx=5)
        Button(
            self.owned_form_frame,
            text="Add to Collection",
            command=self.add_owned_game,
            bootstyle="success-outline",  # type: ignore
        ).grid(row=4, column=0, columnspan=2, pady=5)
        Button(
            self.owned_form_frame,
            text="Import Steam Library",
            command=self.import_steam_library,
            bootstyle="warning-outline",  # type: ignore
        ).grid(row=5, column=0, columnspan=2, pady=5)

        # Recommendations Table
        self.recommend_headers = ["Platform", "Title", "URL", "End Date"]
        self.recommend_labels = [
            Label(
                self.recommend_tab,
                text=h,
                font=("Press Start 2P", 10),
                foreground="#00FFFF",
            )
            for h in self.recommend_headers
        ]
        for i, label in enumerate(self.recommend_labels):
            label.grid(row=0, column=i, padx=5, pady=5, sticky="w")
        Label(
            self.recommend_tab,
            text="Suggested Freebies",
            font=("Orbitron", 14),
            foreground="#00FFFF",
        ).grid(row=1, column=0, columnspan=4, pady=5)

        # Stats Tab
        Label(
            self.stats_tab,
            text="Game Stats",
            font=("Orbitron", 14),
            foreground="#FFD700",
        ).grid(row=0, column=0, pady=5)
        # Chart.js integration handled via main.py

        # Control Buttons
        self.control_frame = Frame(self.main_frame, bootstyle="dark")  # type: ignore
        self.control_frame.pack(pady=10)
        Button(
            self.control_frame,
            text="Refresh Arcade",
            command=self.on_refresh_arcade_button_click,  # Changed command
            bootstyle="danger",  # type: ignore
        ).grid(row=0, column=0, padx=5)

        Button(
            self.control_frame,
            text="Export to CSV",
            command=lambda: self.export_backup.export_to_csv(),
            bootstyle="info-outline", # type: ignore
        ).grid(row=0, column=1, padx=5)

        if self.cloud_sync: # Check if cloud_sync object exists
            Button(
                self.control_frame,
                text="Sync to Cloud",
                command=self.cloud_sync.upload_db,  # This is now safe
                bootstyle="warning-outline",  # type: ignore
            ).grid(row=0, column=2, padx=5)

        # Status Bar
        self.status_var = tk.StringVar()
        Label(
            self.main_frame,
            textvariable=self.status_var,
            font=("Orbitron", 10),
            foreground="#00FFFF",
        ).pack(side="bottom", fill="x")
        self.update_status()

        self.update_gui()

    async def _async_process_single_game(self, game_info: FreeGame):
        """Processes one game: add to DB, get price, tag genre."""
        self.db.add_game(game_info.title, game_info.platform, game_info.url, game_info.end_date)
        # Fetch price and update DB (price_tracker.get_game_price is async)
        await self.price_tracker.get_game_price(game_info.title, game_info.platform)
        # Tag genre and update DB (genre_tagging.tag_game is sync)
        self.genre_tagging.tag_game(game_info.title, game_info.title) # Using title as placeholder description

    def on_refresh_arcade_button_click(self):
        """Handles the 'Refresh Arcade' button click by running the refresh cycle in a new thread."""
        self.root.after(0, lambda: self.status_var.set("Refreshing Arcade... Please wait..."))
        def threaded_task():
            asyncio.run(self._execute_full_refresh_cycle())

        # Ensure a new event loop for the new thread if asyncio.run is used.
        # This is generally handled by asyncio.run itself.
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        thread = threading.Thread(target=threaded_task, daemon=True)
        thread.start()

    async def _execute_full_refresh_cycle(self):
        """
        The comprehensive refresh logic.
        Scrapes games, processes them, updates DB, notifies, and updates GUI.
        """
        try:
            # Scrape main games
            scraped_main_games = await self.scraper.scrape_all()
            for game_info in scraped_main_games:
                await self._async_process_single_game(game_info)

            # Scrape multi-language games (e.g., Epic DE)
            # This directly adds to DB via self.multi_language.ai_module & self.multi_language.db
            await self.multi_language.scrape_non_english(
                "https://store.epicgames.com/de-DE/free-games", "Epic", "de"
            )

            # DB maintenance
            self.db.check_expirations()

            # Notifications
            self.notifications.notify_new_games()
            self.notifications.notify_expiring_games()

            # Final GUI updates (scheduled to run in the main Tkinter thread)
            def final_updates():
                self.update_gui()
                self.update_status()
                self.status_var.set("Arcade refreshed successfully!")
            self.root.after(0, final_updates)

        except Exception as e:
            print(f"Error during refresh cycle: {e}")
            # Schedule error message update to main thread
            self.root.after(0, lambda err=e: self.status_var.set(f"Refresh error: {str(err)[:100]}"))

    def add_owned_game(self):
        title = self.title_entry.get()
        platform = self.platform_entry.get()
        url = self.url_entry.get()
        if title and platform:
            self.owned_games.add_owned_game(title, platform, url)
            self.title_entry.delete(0, tk.END)
            self.platform_entry.set("")
            self.url_entry.delete(0, tk.END)
            self.update_gui()
            self.update_status()

    def import_steam_library(self):
        steam_id = simpledialog.askstring(
            "Steam ID", "Enter your Steam ID:", parent=self.root
        )
        api_key = simpledialog.askstring(
            "API Key", "Enter your Steam API Key:", parent=self.root
        )
        if steam_id and api_key:
            asyncio.run(self.library_import.import_steam_library(steam_id, api_key))
            self.update_gui()
            self.update_status() # This update_status is fine here as it's after asyncio.run

    def update_status(self):
        counts = self.db.get_status_counts()
        owned_count = counts.get("owned", 0)
        claimed_count = counts.get("claimed", 0)
        active_count = counts.get("active", 0)
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(price) FROM games WHERE price IS NOT NULL")
        total_value = cursor.fetchone()[0] or 0
        conn.close()
        self.status_var.set(
            f"Collection: {owned_count} Games | Missions Completed: {claimed_count} | Active Deals: {active_count} | Value: ${total_value:.2f}"
        )

    def update_active_gui(self):
        for widget in self.active_tab.winfo_children()[len(self.active_headers) + 1 :]:
            widget.destroy()
        platform = (
            self.active_platform.get() if self.active_platform.get() != "All" else None
        )
        genre = self.active_genre.get() if self.active_genre.get() != "All" else None
        search_term = self.active_search.get()
        games = self.game_filter.filter_games("active", platform, genre, search_term)
        for row_idx, (platform, title, end_date) in enumerate(games, 2):
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT url, price, genre FROM games WHERE title = ? AND platform = ?",
                (title, platform),
            )
            # Explicitly type hint the expected return from fetchone for this query
            fetched_active_details: tuple[str | None, float | None, str | None] | None = cursor.fetchone()
            conn.close()
            if fetched_active_details:
                url, price, genre = fetched_active_details
            else:
                url, price, genre = None, None, None # Should ideally not happen if game is from filtered list
            Label(
                self.active_tab,
                text=platform,
                font=("Orbitron", 10),
                foreground="#FFFFFF",
            ).grid(row=row_idx, column=0, padx=5, sticky="w")
            Label(
                self.active_tab, text=title, font=("Orbitron", 10), foreground="#FFFFFF"
            ).grid(row=row_idx, column=1, padx=5, sticky="w")
            Button(
                self.active_tab,
                text="Claim",
                command=lambda u=url: self.claim_game(u),
                bootstyle="info-outline",  # type: ignore
            ).grid(row=row_idx, column=2, padx=5)
            Button(
                self.active_tab,
                text="Mark Owned",
                command=lambda t=title, p=platform, u=url: self.mark_owned(t, p, u),
                bootstyle="warning-outline",  # type: ignore
            ).grid(row=row_idx, column=3, padx=5)
            Label(
                self.active_tab,
                text=end_date or "Unknown",
                font=("Orbitron", 10),
                foreground="#FF69B4",
            ).grid(row=row_idx, column=4, padx=5, sticky="w")
            Label(
                self.active_tab,
                text=f"${price:.2f}" if price else "N/A",
                font=("Orbitron", 10),
                foreground="#FFD700",
            ).grid(row=row_idx, column=5, padx=5, sticky="w")
            Label(
                self.active_tab,
                text=genre or "N/A",
                font=("Orbitron", 10),
                foreground="#00FF00",
            ).grid(row=row_idx, column=6, padx=5, sticky="w")

    def update_gui(self):
        for widget in self.active_tab.winfo_children()[len(self.active_headers) + 1 :]:
            widget.destroy()
        for widget in self.claimed_tab.winfo_children()[
            len(self.claimed_headers) + 1 :
        ]:
            widget.destroy()
        for widget in self.expired_tab.winfo_children()[
            len(self.expired_headers) + 1 :
        ]:
            widget.destroy()
        for widget in self.owned_tab.winfo_children()[len(self.owned_headers) + 2 :]:
            widget.destroy()
        for widget in self.recommend_tab.winfo_children()[
            len(self.recommend_headers) + 1 :
        ]:
            widget.destroy()
        for widget in self.stats_tab.winfo_children()[1:]:
            widget.destroy()

        # Active Games (use filter)
        self.update_active_gui()

        # Claimed Games
        for row_idx, (platform, title, claim_date) in enumerate(
            self.db.get_games_by_status("claimed"), 2
        ):
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT price, genre FROM games WHERE title = ? AND platform = ?",
                (title, platform),
            )
            # Explicitly type hint the expected return from fetchone for this query (price, genre)
            fetched_details: tuple[float | None, str | None] | None = cursor.fetchone()
            conn.close()
            # Unpack the fetched details, handling the case where no row was found
            price, genre = fetched_details if fetched_details else (None, None)

            Label(
                self.claimed_tab,
                text=platform,
                font=("Orbitron", 10),
                foreground="#FFFFFF",
            ).grid(row=row_idx, column=0, padx=5, sticky="w")
            Label(
                self.claimed_tab,
                text=title,
                font=("Orbitron", 10),
                foreground="#FFFFFF",
            ).grid(row=row_idx, column=1, padx=5, sticky="w")
            Label(
                self.claimed_tab,
                text=claim_date,
                font=("Orbitron", 10),
                foreground="#00FF00",
            ).grid(row=row_idx, column=2, padx=5, sticky="w")
            Label(
                self.claimed_tab,
                text=f"${price:.2f}" if price else "N/A",
                font=("Orbitron", 10),
                foreground="#FFD700",
            ).grid(row=row_idx, column=3, padx=5, sticky="w")
            Label(
                self.claimed_tab,
                text=genre or "N/A",
                font=("Orbitron", 10),
                foreground="#00FF00",
            ).grid(row=row_idx, column=4, padx=5, sticky="w")

        # Expired Games
        for row_idx, (platform, title, epitaph) in enumerate(
            self.db.get_games_by_status("expired"), 2
        ):
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT price, genre FROM games WHERE title = ? AND platform = ?",
                (title, platform),
            )
            # Explicitly type hint the expected return from fetchone for this query
            fetched_expired_details: tuple[float | None, str | None] | None = cursor.fetchone()
            conn.close()
            if fetched_expired_details:
                price, genre = fetched_expired_details
            else:
                price, genre = None, None
            Label(
                self.expired_tab,
                text=platform,
                font=("Orbitron", 10),
                foreground="#FFFFFF",
            ).grid(row=row_idx, column=0, padx=5, sticky="w")
            Label(
                self.expired_tab,
                text=title,
                font=("Orbitron", 10),
                foreground="#FFFFFF",
            ).grid(row=row_idx, column=1, padx=5, sticky="w")
            Label(
                self.expired_tab,
                text=epitaph,
                font=("Orbitron", 10),
                foreground="#FF4500",
            ).grid(row=row_idx, column=2, padx=5, sticky="w")
            Label(
                self.expired_tab,
                text=f"${price:.2f}" if price else "N/A",
                font=("Orbitron", 10),
                foreground="#FFD700",
            ).grid(row=row_idx, column=3, padx=5, sticky="w")
            Label(
                self.expired_tab,
                text=genre or "N/A",
                font=("Orbitron", 10),
                foreground="#00FF00",
            ).grid(row=row_idx, column=4, padx=5, sticky="w")

        # Owned Games
        for row_idx, (platform, title, acquisition_date) in enumerate(
            self.db.get_games_by_status("owned"), 3
        ):
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT price, genre FROM games WHERE title = ? AND platform = ?",
                (title, platform),
            )
            # Explicitly type hint the expected return from fetchone for this query
            fetched_owned_details: tuple[float | None, str | None] | None = cursor.fetchone()
            conn.close()
            if fetched_owned_details:
                price, genre = fetched_owned_details
            else:
                price, genre = None, None
            Label(
                self.owned_tab,
                image=self.gamepad_icon,
                compound="left",
                text=platform,
                font=("Orbitron", 10),
                foreground="#FFFFFF",
            ).grid(row=row_idx, column=0, padx=5, sticky="w")
            Label(
                self.owned_tab, text=title, font=("Orbitron", 10), foreground="#FFFFFF"
            ).grid(row=row_idx, column=1, padx=5, sticky="w")
            Label(
                self.owned_tab,
                text=acquisition_date,
                font=("Orbitron", 10),
                foreground="#FFD700",
            ).grid(row=row_idx, column=2, padx=5, sticky="w")
            Label(
                self.owned_tab,
                text=f"${price:.2f}" if price else "N/A",
                font=("Orbitron", 10),
                foreground="#FFD700",
            ).grid(row=row_idx, column=3, padx=5, sticky="w")
            Label(
                self.owned_tab,
                text=genre or "N/A",
                font=("Orbitron", 10),
                foreground="#00FF00",
            ).grid(row=row_idx, column=4, padx=5, sticky="w")

        # Recommendations
        for row_idx, (platform, title, url, end_date) in enumerate(
            self.ai_recommendations.recommend_games(), 2
        ):
            Label(
                self.recommend_tab,
                text=platform,
                font=("Orbitron", 10),
                foreground="#FFFFFF",
            ).grid(row=row_idx, column=0, padx=5, sticky="w")
            Label(
                self.recommend_tab,
                text=title,
                font=("Orbitron", 10),
                foreground="#FFFFFF",
            ).grid(row=row_idx, column=1, padx=5, sticky="w")
            Button(
                self.recommend_tab,
                text="Visit",
                command=lambda u=url: webbrowser.open(u),
                bootstyle="info-outline", # type: ignore
            ).grid(row=row_idx, column=2, padx=5)
            Label(
                self.recommend_tab,
                text=end_date or "Unknown",
                font=("Orbitron", 10),
                foreground="#00FFFF",
            ).grid(row=row_idx, column=3, padx=5, sticky="w")

        # Stats (Chart.js placeholder)
        # chart = self.analytics.get_platform_chart() # This variable was assigned but not used.
        Label(
            self.stats_tab,
            text="Platform Distribution",
            font=("Orbitron", 12),
            foreground="#FFD700",
        ).grid(row=1, column=0, pady=5)
        # Chart.js rendering handled by frontend integration

    def claim_game(self, url):
        webbrowser.open(url)
        if messagebox.askyesno(
            "Claimed?", "Did you claim this game?", parent=self.root
        ):
            self.db.mark_game_claimed(url)
            if messagebox.askyesno(
                "Owned?", "Is this game now in your library?", parent=self.root
            ):
                conn = sqlite3.connect(self.db.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT title, platform, url FROM games WHERE url = ?", (url,)
                )
                # Explicitly type hint the expected return from fetchone for this query
                fetched_claim_details: tuple[str | None, str | None, str | None] | None = cursor.fetchone()
                conn.close()
                if fetched_claim_details:
                    title_claimed, platform_claimed, url_claimed = fetched_claim_details
                    self.owned_games.add_owned_game(title_claimed, platform_claimed, url_claimed)
                else:
                    # Handle case where game is not found by URL after claiming, though unlikely
                    print(f"Warning: Could not find game by URL {url} after claiming.")
            self.update_gui()
            self.update_status()

    def mark_owned(self, title, platform, url):
        self.owned_games.add_owned_game(title, platform, url)
        self.update_gui()
        self.update_status()

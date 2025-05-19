# Game Tracker & Free Games Arcade

This project is a comprehensive tool for tracking free games from various platforms, managing your game library, getting AI-powered recommendations, and more. It features a desktop GUI application, data scraping capabilities, and an AI module for classification and recommendations.

## Features

*   **Free Game Scraping:** Automatically fetches free game deals from Epic Games, Amazon Prime, GOG, Ubisoft, Itch.io, IndieGala, and Humble Bundle.
*   **Game Library Management:** Keep track of active deals, claimed games, owned games, and expired deals.
*   **AI-Powered Features:**
    *   Classify text to determine if it describes a free game (trainable).
    *   Generate text embeddings for game titles.
    *   Provide game recommendations based on your owned library.
*   **Notifications:** Get desktop and email notifications for new and expiring free games.
*   **Price Tracking:** Fetch current game prices from IsThereAnyDeal.
*   **Library Import:** Import your Steam library.
*   **Data Export/Backup:** Export your game data to CSV or JSON.
*   **Optional Cloud Sync:** Synchronize your game database with AWS S3.
*   **GUI Application:** A user-friendly desktop interface built with Tkinter and ttkbootstrap.
*   **Data Labeling Tool:** A separate GUI tool to help create and refine datasets for AI model training.
*   **Analytics:** View basic statistics about your game collection.

## Project Structure & File Explanations

Here's a breakdown of the key files in this project:

*   `main.py`: The main entry point for the Game Tracker application. It initializes all components (database, AI, scrapers, GUI, etc.) and starts the application.
*   `gui.py`: Defines the `FreeGamesGUI` class, which builds and manages the graphical user interface using Tkinter and ttkbootstrap. It handles user interactions and displays game data across various tabs.
*   `db_manager.py`: The `DBManager` class handles all interactions with the SQLite database (`free_games.db`). This includes creating tables, adding games, updating game statuses, and querying game data.
*   `scraper.py`: Contains the `GameScraper` class, responsible for asynchronously scraping free game information from various online platforms like Epic Games, Amazon Prime, GOG, etc. It uses `aiohttp` and `BeautifulSoup` (and `playwright` for Ubisoft).
*   `ai_module.py`: The `AIModule` class manages the AI model (DistilBERT). It's responsible for:
    *   Loading a pre-trained or fine-tuned model.
    *   Training the model for text classification (e.g., to identify if a text snippet describes a free game) using a `dataset.jsonl` file.
    *   Providing a pipeline for text classification.
    *   Generating text embeddings for similarity tasks (used in recommendations).
*   `ai_recommendations.py`: The `AIRecommendations` class uses game title embeddings (from `AIModule`) to calculate similarities and recommend active free games based on the user's owned game library.
*   `multi_language.py`: The `MultiLanguage` class is designed to scrape game information from non-English sources (e.g., Epic Games German store). It currently uses `BeautifulSoup` for HTML parsing.
*   `genre_tagging.py`: The `GenreTagging` class is a placeholder for genre tagging functionality. The current AI module is not set up for direct genre extraction from text.
*   `price_tracker.py`: The `PriceTracker` class fetches current game prices from isthereanydeal.com to enrich game data.
*   `library_import.py`: The `LibraryImport` class handles importing game libraries from external platforms, currently supporting Steam (via API). Epic Games import is a placeholder.
*   `owned_games.py`: The `OwnedGames` class provides helper functions for managing games marked as "owned" in the database.
*   `game_filter.py`: The `GameFilter` class allows filtering of games displayed in the GUI based on criteria like status, platform, genre, and search terms.
*   `notifications.py`: The `Notifications` class sends desktop notifications (using `plyer`) and email notifications (using `smtplib`) for new free games and games that are about to expire.
*   `export_backup.py`: The `ExportBackup` class provides functionality to export the game database to CSV and JSON file formats.
*   `cloud_sync.py`: The `CloudSync` class handles optional synchronization of the `free_games.db` database file with an AWS S3 bucket.
*   `analytics.py`: The `Analytics` class generates data structures suitable for creating charts (e.g., distribution of owned games by platform).
*   `wishlist.py`: The `Wishlist` class can check a user's Steam wishlist for any games that have become free.
*   `playtime.py`: The `Playtime` class fetches Steam game playtime using the Steam API.
*   `community_sharing.py`: The `CommunitySharing` class is intended for sharing free game deals to platforms like Discord via webhooks.
*   `offline_mode.py`: The `OfflineMode` class provides functionality to cache game data to a JSON file for offline viewing.
*   `generate_dataset.py`: This script is crucial for AI model training. It scrapes various websites (Epic, Amazon, GOG, etc.) and X (Twitter) posts to create a `dataset.jsonl` file. This dataset contains text samples and labels (is\_free, title, URL, end\_date) used by the `labeling_tool.py` and for training the `AIModule`.
*   `labeling_tool.py`: A standalone Tkinter GUI application that loads samples (typically from `generate_dataset.py`) and allows a user to view, verify, and correct labels. The output is saved to `dataset.jsonl`, which is then used to train the AI model in `ai_module.py`.
*   `stats_chart.py`: This script loads the `dataset.jsonl` file, calculates statistics about the labeled data (e.g., free vs. non-free samples per platform), and generates a configuration dictionary for a Chart.js bar chart. This is used by the `labeling_tool.py` to display dataset statistics.

## Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd Game_Tracker
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    # On Windows
    .venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    You will need to install several Python libraries. Create a `requirements.txt` file with the following content:
    ```txt
    aiohttp
    beautifulsoup4
    pydantic
    playwright
    transformers
    datasets
    torch
    scikit-learn
    ttkbootstrap
    Pillow
    plyer
    apscheduler
    boto3
    # For labeling_tool.py and stats_chart.py
    pygame
    # tkinterweb is not a standard PyPI package, ensure it's correctly installed if used by HtmlFrame
    # If tkinterweb is from a specific source, add installation instructions here.
    # For now, assuming it's available or part of ttkbootstrap/tkinter.
    ```
    Then install them:
    ```bash
    pip install -r requirements.txt
    ```
    You also need to install Playwright's browser drivers:
    ```bash
    python -m playwright install
    playwright install
    ```

4.  **Configuration (Optional but Recommended):**
    *   **Notifications:** Update email settings in `main.py` within the `Notifications` instantiation if you want email alerts.
    *   **Cloud Sync:** If using AWS S3 sync, set `ENABLE_CLOUD_SYNC = True` in `main.py` and provide your AWS credentials and bucket name. **It's highly recommended to use environment variables or a secure config file for credentials instead of hardcoding.**
    *   **Steam API Key:** For Steam library import, wishlist checking, and playtime, you'll be prompted for your Steam ID and API key in the GUI.

## How to Run

### 1. Generate Dataset for AI (Optional, but needed for AI training/labeling)

This script scrapes various sources to create `dataset.jsonl`, which is used by the labeling tool and for training the AI.

```bash
python generate_dataset.py
```
This will create/overwrite `dataset.jsonl` in the project root.

### 2. Label the Dataset (Optional, but recommended for AI accuracy)

The labeling tool allows you to review and correct the data scraped by `generate_dataset.py`.

```bash
python labeling_tool.py
```
This will open a GUI. Use it to verify and save labels. The output is `dataset.jsonl`.

### 3. Train the AI Model (Optional, if you want to use custom AI classification)

After generating and labeling your dataset, you can train the AI model.
You'll need to trigger this from a Python script or by adding a temporary call in `main.py` before the GUI starts. For example, in `main.py`, before `root = Window()`:

```python
# In main.py (temporary addition for training)
# ...
if __name__ == "__main__":
    db = DBManager()
    ai = AIModule()
    # --- Add this line to train ---
    # Ensure 'dataset.jsonl' exists from previous steps
    # ai.train("dataset.jsonl")
    # --- End of training line ---
    scraper = GameScraper(ai_module=ai)
# ...
```
Run `python main.py` once with this line uncommented. Then, comment it out again for normal operation. The trained model will be saved to the `distilbert-free-games` directory.

### 4. Run the Main Game Tracker Application

This is the primary application with the GUI.

```bash
python main.py
```

The application will start, create `free_games.db` if it doesn't exist, and the GUI will appear. The scrapers will run on a schedule (and can be triggered manually via the "Refresh Arcade" button).

## Notes

*   **Web Scraping:** Scrapers can break if website structures change. They may need periodic updates.
*   **AI Model:** The default AI model is `distilbert-base-uncased`. Fine-tuning it with your own labeled data (steps 1-3 above) will improve its accuracy for classifying free game descriptions.
*   **API Keys:** Features like Steam library import, wishlist, and playtime require a Steam API key.
*   **Error Handling:** The project includes basic error handling, but further enhancements can always be made.

```
## Packaging the Application
Package: Use PyInstaller:
bash
pyinstaller --add-data "gamepad.png;." main.py

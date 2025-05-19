import tkinter as tk
from tkinter import ttk, messagebox
import json
import asyncio
import re
from tkinterweb.htmlwidgets import HtmlFrame
from generate_dataset import (
    scrape_epic_games,
    scrape_amazon_prime,
    scrape_gog,
    scrape_steam_non_free,
    scrape_ubisoft,
    scrape_itch_io,
    scrape_indiegala,
    scrape_humble_bundle,
    scrape_x_posts,
)
from stats_chart import generate_chart_config
from datetime import datetime
import pygame


class LabelingTool:
    def __init__(self, samples, output_file="dataset.jsonl"):
        self.samples = samples
        self.output_file = output_file
        self.index = 0
        self.filtered_samples = samples
        self.platforms = [
            "All",
            "Epic",
            "Amazon",
            "GOG",
            "Steam",
            "Ubisoft",
            "Itch.io",
            "IndieGala",
            "Humble",
            "X",
        ]
        self.root = tk.Tk()
        self.root.title("Cyberpunk Dataset Labeling Tool")
        self.root.configure(bg="#1a1a1a")
        pygame.mixer.init()
        try:
            self.click_sound = pygame.mixer.Sound("click.wav")
        except FileNotFoundError:
            print("Warning: click.wav not found, sound effects disabled")
            self.click_sound = None
        self.setup_gui()
        self.root.geometry("800x600")

    def setup_gui(self):
        # Style
        style = ttk.Style()
        style.configure(
            "Cyber.TButton",
            font=("Courier", 10),
            background="#00ffcc",
            foreground="#000000",
        )
        style.configure(
            "Cyber.TLabel",
            font=("Courier", 10),
            background="#1a1a1a",
            foreground="#00ffcc",
        )
        style.configure("Cyber.TEntry", font=("Courier", 10))
        style.configure("Cyber.TCombobox", font=("Courier", 10))

        # Notebook (tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(pady=10, fill="both", expand=True)

        # Labeling tab
        labeling_frame = tk.Frame(notebook, bg="#1a1a1a")
        notebook.add(labeling_frame, text="Labeling")

        # Stats tab
        stats_frame = tk.Frame(notebook, bg="#1a1a1a")
        notebook.add(stats_frame, text="Stats")

        # Labeling frame setup
        main_frame = tk.Frame(labeling_frame, bg="#1a1a1a")
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Platform filter
        ttk.Label(main_frame, text="Platform Filter:", style="Cyber.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self.platform_var = tk.StringVar(value="All")
        platform_dropdown = ttk.Combobox(
            main_frame,
            textvariable=self.platform_var,
            values=self.platforms,
            style="Cyber.TCombobox",
        )
        platform_dropdown.grid(row=0, column=1, sticky="w")
        platform_dropdown.bind("<<ComboboxSelected>>", self.filter_samples)

        # Progress bar
        self.progress = ttk.Progressbar(
            main_frame, maximum=len(self.samples), mode="determinate"
        )
        self.progress.grid(row=1, column=0, columnspan=3, sticky="ew", pady=5)
        self.progress_label = ttk.Label(main_frame, text="0/0", style="Cyber.TLabel")
        self.progress_label.grid(row=1, column=3, sticky="w")

        # Text display
        ttk.Label(main_frame, text="Text:", style="Cyber.TLabel").grid(
            row=2, column=0, sticky="w"
        )
        self.text_label = tk.Label(
            main_frame,
            text="",
            wraplength=600,
            font=("Courier", 10),
            bg="#1a1a1a",
            fg="#ffffff",
            justify="left",
        )
        self.text_label.grid(row=2, column=1, columnspan=2, sticky="w")

        # Input fields
        ttk.Label(main_frame, text="Is Free (0/1):", style="Cyber.TLabel").grid(
            row=3, column=0, sticky="w"
        )
        self.is_free_entry = ttk.Entry(main_frame, style="Cyber.TEntry")
        self.is_free_entry.grid(row=3, column=1, sticky="w")

        ttk.Label(main_frame, text="Title:", style="Cyber.TLabel").grid(
            row=4, column=0, sticky="w"
        )
        self.title_entry = ttk.Entry(main_frame, style="Cyber.TEntry")
        self.title_entry.grid(row=4, column=1, sticky="w")

        ttk.Label(main_frame, text="URL:", style="Cyber.TLabel").grid(
            row=5, column=0, sticky="w"
        )
        self.url_entry = ttk.Entry(main_frame, style="Cyber.TEntry")
        self.url_entry.grid(row=5, column=1, sticky="w")

        ttk.Label(main_frame, text="End Date (YYYY-MM-DD):", style="Cyber.TLabel").grid(
            row=6, column=0, sticky="w"
        )
        self.end_date_entry = ttk.Entry(main_frame, style="Cyber.TEntry")
        self.end_date_entry.grid(row=6, column=1, sticky="w")

        # Buttons
        ttk.Button(
            main_frame,
            text="Save & Next",
            command=self.save_sample,
            style="Cyber.TButton",
        ).grid(row=7, column=1, pady=10, sticky="w")
        ttk.Button(
            main_frame, text="Skip", command=self.skip_sample, style="Cyber.TButton"
        ).grid(row=7, column=2, pady=10, sticky="w")
        ttk.Button(
            main_frame,
            text="Clear Dataset",
            command=self.clear_dataset,
            style="Cyber.TButton",
        ).grid(row=8, column=1, pady=10, sticky="w")

        # Stats frame setup
        self.stats_html = HtmlFrame(stats_frame, messages_enabled=False)
        self.stats_html.pack(fill="both", expand=True)
        self.update_stats_chart()

        self.update_display()

    def update_stats_chart(self):
        chart_config = generate_chart_config(self.output_file)
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {{ background-color: #1a1a1a; }}
                canvas {{ max-width: 100%; }}
            </style>
        </head>
        <body>
            <canvas id="statsChart"></canvas>
            <script>
                const ctx = document.getElementById('statsChart').getContext('2d');
                new Chart(ctx, {json.dumps(chart_config)});
            </script>
        </body>
        </html>
        """
        self.stats_html.load_html(html_content)

    def filter_samples(self, event=None):
        selected_platform = self.platform_var.get()
        if selected_platform == "All":
            self.filtered_samples = self.samples
        else:
            self.filtered_samples = [
                s
                for s in self.samples
                if selected_platform.lower() in s["text"].lower()
            ]
        self.index = 0
        self.progress.configure(maximum=len(self.filtered_samples))
        self.update_display()

    def update_display(self):
        if self.index < len(self.filtered_samples):
            self.text_label.config(text=self.filtered_samples[self.index]["text"])
            self.is_free_entry.delete(0, tk.END)
            self.title_entry.delete(0, tk.END)
            self.url_entry.delete(0, tk.END)
            self.end_date_entry.delete(0, tk.END)
            labels = self.filtered_samples[self.index].get("labels", {})
            self.is_free_entry.insert(0, labels.get("is_free", ""))
            self.title_entry.insert(0, labels.get("title", ""))
            self.url_entry.insert(0, labels.get("url", ""))
            self.end_date_entry.insert(0, labels.get("end_date", ""))
            self.progress["value"] = self.index
            self.progress_label.config(
                text=f"{self.index+1}/{len(self.filtered_samples)}"
            )
        else:
            messagebox.showinfo(
                "Done", "All samples labeled! Dataset saved to dataset.jsonl"
            )
            self.root.quit()

    def is_valid_url(self, url):
        return (
            not url.endswith("/p/[]") and bool(re.match(r"https?://[^\s]+", url))
            if url
            else True
        )

    def validate_inputs(self):
        try:
            is_free = self.is_free_entry.get()
            if is_free and int(is_free) not in [0, 1]:
                raise ValueError("Is Free must be 0 or 1")
            end_date = self.end_date_entry.get()
            if end_date:
                datetime.strptime(end_date, "%Y-%m-%d")
            url = self.url_entry.get()
            if not self.is_valid_url(url):
                raise ValueError("Invalid URL format")
            title = self.title_entry.get()
            if not title or title.strip() == "":
                raise ValueError("Title cannot be empty")
            return True
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return False

    def save_sample(self):
        if self.click_sound:
            self.click_sound.play()
        if not self.validate_inputs():
            return
        if self.index < len(self.filtered_samples):
            sample = self.filtered_samples[self.index]
            sample["labels"] = {
                "is_free": (
                    int(self.is_free_entry.get()) if self.is_free_entry.get() else 0
                ),
                "title": self.title_entry.get(),
                "url": self.url_entry.get(),
                "end_date": self.end_date_entry.get(),
            }
            # Check for duplicates
            try:
                with open(self.output_file, "r", encoding="utf-8") as f:
                    existing = {json.loads(line)["text"] for line in f if line.strip()}
            except FileNotFoundError:
                existing = set()
            if sample["text"] not in existing:
                with open(self.output_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(sample) + "\n")
                self.update_stats_chart()
            self.index += 1
            self.update_display()

    def skip_sample(self):
        if self.click_sound:
            self.click_sound.play()
        if self.index < len(self.filtered_samples):
            self.index += 1
            self.update_display()

    def clear_dataset(self):
        if self.click_sound:
            self.click_sound.play()
        if messagebox.askyesno(
            "Confirm", "Clear dataset.jsonl? This cannot be undone."
        ):
            open(self.output_file, "w", encoding="utf-8").close()
            messagebox.showinfo("Success", "dataset.jsonl cleared")
            self.update_stats_chart()


async def load_samples():
    scrapers = [
        scrape_epic_games,
        scrape_amazon_prime,
        scrape_gog,
        scrape_steam_non_free,
        scrape_ubisoft,
        scrape_itch_io,
        scrape_indiegala,
        scrape_humble_bundle,
        scrape_x_posts,
    ]
    samples = []
    for scraper in scrapers:
        try:
            scraper_samples = await scraper()
            samples.extend(scraper_samples)
        except Exception as e:
            print(f"Error in {scraper.__name__}: {e}")
    return samples


if __name__ == "__main__":
    samples = asyncio.run(load_samples())
    app = LabelingTool(samples)
    app.root.mainloop()

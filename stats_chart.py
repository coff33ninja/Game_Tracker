import json
from collections import defaultdict


def load_dataset_stats(dataset_file="dataset.jsonl"):
    stats = defaultdict(lambda: {"free": 0, "non_free": 0})
    platforms = [
        "Epic",
        "Amazon",
        "GOG",
        "Ubisoft",
        "Itch.io",
        "IndieGala",
        "X",
        "Manual",
    ]

    with open(dataset_file, "r", encoding="utf-8") as f:
        for line in f:
            sample = json.loads(line.strip())
            text = sample["text"]
            is_free = sample["labels"]["is_free"]

            platform = "Manual"
            for p in platforms[:-1]:
                if p.lower() in text.lower():
                    platform = p
                    break

            if is_free:
                stats[platform]["free"] += 1
            else:
                stats[platform]["non_free"] += 1

    return stats


def generate_chart_config(dataset_file="dataset.jsonl"):
    stats = load_dataset_stats(dataset_file)
    labels = list(stats.keys())
    free_data = [stats[p]["free"] for p in labels]
    non_free_data = [stats[p]["non_free"] for p in labels]

    return {
        "type": "bar",
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "label": "Free Games",
                    "data": free_data,
                    "backgroundColor": "#00ffcc",
                    "borderColor": "#00cc99",
                    "borderWidth": 1,
                },
                {
                    "label": "Non-Free Games",
                    "data": non_free_data,
                    "backgroundColor": "#ff3366",
                    "borderColor": "#cc0033",
                    "borderWidth": 1,
                },
            ],
        },
        "options": {
            "scales": {
                "y": {
                    "beginAtZero": True,
                    "title": {
                        "display": True,
                        "text": "Number of Samples",
                        "color": "#ffffff",
                    },
                    "ticks": {"color": "#ffffff"},
                },
                "x": {
                    "title": {"display": True, "text": "Platform", "color": "#ffffff"},
                    "ticks": {"color": "#ffffff"},
                },
            },
            "plugins": {
                "legend": {"labels": {"color": "#ffffff"}},
                "title": {
                    "display": True,
                    "text": "Free vs Non-Free Games by Platform",
                    "color": "#00ffcc",
                    "font": {"size": 18},
                },
            },
        },
    }


if __name__ == "__main__":
    config = generate_chart_config()
    print(json.dumps(config, indent=2))

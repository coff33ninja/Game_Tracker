# ai_module.py
from transformers.models.distilbert import DistilBertTokenizer, DistilBertForSequenceClassification
from transformers.pipelines import pipeline
from transformers.trainer import Trainer
from transformers.training_args import TrainingArguments
from datasets import load_dataset # Dataset class itself is not directly used here
import torch
import os


class AIModule:
    def __init__(self, model_path="distilbert-free-games"):
        self.tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Device set to use {self.device}")

        # Check if a fine-tuned model exists
        config_path = os.path.join(model_path, "config.json")
        model_weights_path = os.path.join(model_path, "pytorch_model.bin")

        if os.path.exists(model_path) and os.path.exists(config_path) and os.path.exists(model_weights_path):
            self.model = DistilBertForSequenceClassification.from_pretrained(model_path)
            print(f"Loaded fine-tuned model from {model_path}")
        else:
            print("Initializing new model from distilbert-base-uncased for sequence classification (2 labels).")
            # Initialize for binary classification (e.g., FREE vs NOT_FREE)
            self.model = DistilBertForSequenceClassification.from_pretrained(
                "distilbert-base-uncased",
                num_labels=2, # For "is_free": 0 or 1
                id2label={0: "NOT_FREE", 1: "FREE"}, # Makes pipeline output more readable
                label2id={"NOT_FREE": 0, "FREE": 1}
            )
        self.model.to(self.device) # type: ignore

        # Use integer for pipeline device: -1 for CPU, 0, 1, ... for GPU
        pipeline_device = self.device.index if self.device.type == "cuda" else -1
        self.nlp = pipeline(
            "text-classification", # Correct pipeline for sequence classification
            model=self.model,
            tokenizer=self.tokenizer,
            device=pipeline_device,
        )

    def train(self, dataset_path):
        dataset = load_dataset("json", data_files=dataset_path)
        # Example dataset format:
        # [{"text": "Free on Epic: Dead Island 2", "labels": {"title": "Dead Island 2", "url": "https://store.epicgames.com/...", "is_free": 1}}, ...]

        # Tokenize and prepare data
        def preprocess_function(examples):
            # Tokenize the texts
            tokenized_inputs = self.tokenizer(
                examples["text"], padding="max_length", truncation=True, max_length=512
            )
            # Extract the 'is_free' field from the 'labels' dictionary to be the actual training label
            tokenized_inputs["label"] = [label_dict["is_free"] for label_dict in examples["labels"]]
            return tokenized_inputs

        # Apply preprocessing
        # remove_columns is important to drop the original 'text' and 'labels' (dict) columns
        dataset = dataset.map(preprocess_function, batched=True, remove_columns=["text", "labels"])
        dataset.set_format("torch", columns=["input_ids", "attention_mask", "label"]) # type: ignore # 'label' is now the target

        # Training arguments
        training_args = TrainingArguments(
            output_dir="./results",
            num_train_epochs=3,
            per_device_train_batch_size=8,  # Adjust based on your GPU memory
            per_device_eval_batch_size=8,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir="./logs",
            logging_steps=10,
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=dataset["train"], # type: ignore
            eval_dataset=dataset.get("validation") or dataset.get("test"), # type: ignore # Use test if validation is not present
        )
        trainer.train()
        self.model.save_pretrained("distilbert-free-games")
        self.tokenizer.save_pretrained("distilbert-free-games") # Good practice to save tokenizer with model
        print("Model training complete and saved to 'distilbert-free-games'.")

        # Re-initialize pipeline with the newly trained model and correct device
        pipeline_device = self.device.index if self.device.type == "cuda" else -1
        self.nlp = pipeline("text-classification", model=self.model, tokenizer=self.tokenizer, device=pipeline_device)

    def parse_text(self, text):
        """
        Classifies if the input text indicates a free game.
        Returns a dictionary like: {"is_free": True/False, "score": probability}
        """
        results = self.nlp(text)
        # The 'text-classification' pipeline output is typically a list of dictionaries,
        # e.g., [{'label': 'FREE', 'score': 0.998}]
        if results and isinstance(results, list) and len(results) > 0:
            top_result = results[0]
            predicted_label_str = top_result.get("label")
            score = top_result.get("score")
            # Check against the 'FREE' label defined in id2label/label2id
            is_free_prediction = (predicted_label_str == "FREE")
            return {"is_free": is_free_prediction, "score": score}
        # Default return if classification is inconclusive or fails
        return {"is_free": False, "score": 0.0}

    def get_embedding(self, text):
        """
        Generates a text embedding using the model's base DistilBERT encoder.
        This is useful for semantic similarity tasks.
        """
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()} # Move inputs to the correct device

        self.model.eval() # Ensure model is in evaluation mode for inference
        with torch.no_grad(): # Disable gradient calculations for inference
            # Access the base DistilBERT model (without the classification head)
            outputs = self.model.distilbert(**inputs)
            last_hidden_states = outputs.last_hidden_state

        # Use mean pooling of the last hidden states to get a single sentence embedding
        # This averages the embeddings of all tokens in the sequence.
        sentence_embedding = torch.mean(last_hidden_states, dim=1)
        return sentence_embedding.cpu().numpy() # Return as a NumPy array on CPU

# Current Features Status (v1.0)

This document outlines the functionalities currently implemented in Project Locus.

### 🧠 Core Engine & AI
* **Neural Network Integration:** Intent classification using a model trained on a custom `intents.json` dataset.
* **NLP Preprocessing:** Text tokenization and stemming powered by `nltk` for accurate pattern matching.
* **Automated Training:** Built-in training module that allows the "brain" to update and reload without restarting the entire application.

### 🎙️ Voice & Interaction
* **Background Listener:** Multithreaded voice capture that monitors for the "Locus" wake word without blocking the UI.
* **Manual Activation:** "Click-to-listen" feature via GUI for environments where voice triggers might be impractical.
* **Dynamic UI Feedback:** A `tkinter`-based interface that changes visual states (images and labels) to reflect if the bot is Listening, Thinking, or Training.

### 🌐 Browser & Profile Management
* **Intent-Based Actions:** Capability to recognize and execute commands like opening browsers or specific websites (YouTube).
* **Profile Switching:** Specialized logic to launch applications with specific user profiles (e.g., Anton, Mr. Clean, Default).

### 🛠️ Technical Architecture
* **Multithreading:** Separation of the GUI thread from processing tasks to ensure a smooth, lag-free user experience.
* **Modular Design:** Separated concerns between UI management (`ui_manager.py`), logic processing (`processor.py`), and neural network structure (`model.py`).
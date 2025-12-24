# Automated X (Twitter) Content Pipeline

A two-part Python automation system that generates AI content using Google Gemini and automatically posts the latest results to X (formerly Twitter).

---

## - File Overview

### 1. textgenai.py
**Purpose:** Generates content using the Gemini 2.5 Flash model.
* **How it works:** Combines a system prompt (sys_prompt.txt) and an optional user prompt (user_prompt.txt).
* **Output:** Saves a timestamped .txt file (e.g., Response_YYYY-MM-DD_HH-MM-SS.txt) into a designated generated_texts folder.

### 2. uploader.py
**Purpose:** Authenticates with the X API and handles the posting logic.
* **Automatic Mode:** Scans the target directory, identifies the most recent file based on the filename timestamp, and posts its content.
* **Manual Mode:** Accepts a specific file path as a command-line argument to post a specific draft.

---

## - Setup & Usage

###  Environment Variables
Ensure the following keys are set in your environment:
* GOOGLE_API_KEY: For Gemini AI access.
* X_API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET: For X API (Tweepy) authentication.

###  Running the Pipeline

1. **Generate Content:**
   ```bash
   python textgenai.py

2. **Upload**
   ```bash
   python uploader.py

```markdown
<div align="center">

# 🦅 Crowable
**State-of-the-Art (SOTA) AI-Powered Codebase Extractor**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/downloads/)
[![Powered by Gemini](https://img.shields.io/badge/Powered_by-Google_Gemini-8A2BE2.svg)](https://ai.google.dev/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

*Stop manually copy-pasting code into ChatGPT. Let AI compress your entire repository into a single, token-optimized text file.*

</div>

---

## 📖 Overview

Welcome to **Crowable**! 

If you've ever tried to feed an entire project to an AI model (like ChatGPT, Claude, or Gemini) to ask for a refactor or bug fix, you know the struggle. You hit token limits, you accidentally upload `node_modules` or `.git` folders, and the AI loses context.

**Crowable solves this.** It is an intelligent, high-speed CLI tool that scans your project directory, uses Google's powerful **Gemini AI** to figure out what files are useless noise, and asynchronously extracts only the *core, proprietary source code*. It outputs a beautiful, human-readable (and LLM-readable) text artifact that you can instantly drop into any AI assistant.

Whether you are a seasoned software architect or a non-technical manager trying to understand a codebase, Crowable does the heavy lifting for you.

---

## ✨ Key Features

- 🧠 **AI-Powered Filtering:** Uses Google Gemini 2.5 Flash to dynamically identify and ignore build artifacts, lock files, and useless dependencies.
- ⚡ **Asynchronous Extraction:** Built on Python's `asyncio`, it reads hundreds of files concurrently for blazing-fast performance.
- 🛡️ **Smart Truncation Algorithm:** Automatically collapses massive directories (like `node_modules` or `venv`) in the project roadmap so you don't waste valuable AI tokens.
- 🎨 **Beautiful Terminal UI:** Powered by the `rich` library, featuring live spinning progress bars, dynamic tables, and real-time status updates.
- 📦 **Versioned Output:** Automatically groups your extractions into timestamped folders (`/crowable_output/Project_YYYY-MM-DD_HH-MM/`) keeping your workspace clean.

---

## 🚀 For Beginners: "Zero to Hero" Setup

Don't have a Computer Science degree? Never used the terminal before? **No problem.** Follow these 4 easy steps to get Crowable running on your machine.

### Step 1: Install Python
You need Python to run this tool. 
- Go to [Python.org](https://www.python.org/downloads/) and download the latest version for your operating system.
- **CRITICAL (Windows Users):** When the installer opens, make sure to check the box that says **"Add Python to PATH"** before clicking Install.

### Step 2: Get a Free Google Gemini API Key
Crowable uses Google's AI brain, which requires a "key" to access.
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click **"Get API key"** on the left menu.
4. Click **"Create API key"** and copy the long string of letters and numbers it gives you. Keep this secret!

### Step 3: Download and Setup Crowable
Open your computer's terminal (Command Prompt on Windows, Terminal on Mac) and run these commands one by one:

```bash
# 1. Download the code to your computer
git clone https://github.com/Med-Gh-TN/Crawable.git

# 2. Go into the project folder
cd Crawable

# 3. Install the required packages
pip install -r requirements.txt
```

### Step 4: Add Your API Key
1. Open the Crowable folder on your computer.
2. Navigate to `src/config.py` and open it with any text editor (Notepad, VS Code, TextEdit).
3. Find the line that says `API_KEY = "YOUR_API_KEY_HERE"`.
4. Replace `YOUR_API_KEY_HERE` with the key you got from Google in Step 2. (Keep the quotation marks!)
5. Save the file. You're ready to go!

---

## 💻 Usage

Using Crowable is incredibly simple. Open your terminal and run the main script, followed by the path of the folder you want to analyze.

**Command:**
```bash
python main.py /path/to/your/target/project
```

*(Tip: You can literally drag and drop a folder from your desktop into the terminal window to automatically paste its path!)*

**Expected Output:**
The terminal will display a gorgeous dashboard as it works through the 4 phases. Once complete, look inside the `crowable_output/` folder. You will find:
1. `project_roadmap.txt`: A clean, tree-like map of the project.
2. `source_code.txt`: The consolidated, purely filtered code ready to be fed to an AI.
3. `prompt.txt`: A base prompt template you can use to start your AI conversation.

---

## 🏗️ Under the Hood (Architecture)

For the technical folks, Crowable operates on a highly decoupled, service-oriented architecture:

1. **Phase 1: Structural Crawl (`AsyncFileSystemService`)**
   Generates a pre-filtered map of the directory, instantly applying `HARDCODED_EXCLUSIONS` (mathematically guaranteed noise) and our Smart Truncation algorithm.
2. **Phase 2: Intelligent AI Filtering (`GeminiFilterService`)**
   Passes the roadmap to `gemini-2.5-flash` with a strict JSON schema prompt to dynamically identify project-specific noise. Includes exponential backoff and retry logic for API resilience.
3. **Phase 3: Targeted Extraction (`AsyncCodeExtractorService`)**
   Fires off non-blocking `asyncio.gather` tasks to read all approved files concurrently, updating the `rich` UI progress bar in real-time.
4. **Phase 4: Output Generation**
   Orchestrated by `CrowablePipeline`, saving versioned artifacts to the file system.

---

## 🤝 Contributing

We want Crowable to be the absolute standard for AI code extraction. Contributions from developers of all skill levels are highly welcomed!

**How to contribute:**
1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

> **Note:** If you find a bug or have a feature request, please open an Issue first so we can discuss it!

---

## 📜 License

Distributed under the Apache 2.0 License. See `LICENSE` for more information. This grants you the freedom to use, modify, and distribute the software, even commercially, under the terms of the license.

---

## 👨‍💻 Author

**Mouhamed Gharsallah** 
- GitHub: [@Med-Gh-TN](https://github.com/Med-Gh-TN)

*Built with ❤️ for the open-source community. Let's make AI collaboration seamless.*
```

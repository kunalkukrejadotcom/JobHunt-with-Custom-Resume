# Resume Optimizer & Application Tracker 🚀
*Authored entirely by AI via Google Antigravity* ✨

A self-contained, lightweight Python application that acts as your personal Executive Recruiter. It dynamically ingests your master profile and leverages AI to generate highly tailored, ATS-optimized Markdown resumes for specific job listings on the fly. 

This project strictly adheres to an ultra-lightweight **zero-dependency architecture**—there relies on no React, no Node.js, and no complex SQL databases. The entire dashboard runs locally powered purely by Python's built-in HTTP server, utilizing flat files (`.csv` and `.json`) for high-speed tracking and data privacy.

## ✨ Features
- **PDF Profile Bootstrapping**: Upload your existing PDF resume just once, and the AI automatically structures and parses it into a central `master_profile.json` source of truth.
- **Smart Job Scraping**: Just paste a LinkedIn or company careers URL. The app uses the advanced Jina Reader API to natively scrape the markdown and extract the precise Company Name, Role, and Required Skills immediately.
- **Interactive Keyword Curation**: Before generation, you retain full human-in-the-loop control over exactly which required keywords you actually possess, explicitly preventing AI hallucination.
- **Dual ATS Scoring Engine**: Sceen your Application Readiness! The tool returns two distinct match scores (0-100%): one evaluating your raw `master_profile` against the job requirements, and one final score evaluating your newly formulated Tailored Markdown Resume.
- **Application History Tracking**: Automatically saves every generated job to its own local folder (`applications/{Company}_{Role}_{Date}`) and seamlessly logs your ATS scores to an internal dashboard-accessible `application_tracker.csv`.
- **Dynamic AI Configuration**: Readily utilizes standard vs reasoning backend engines. Fully customizable `MODEL`, `TEMPERATURE`, and API parameters right out of `.config.json`.

## 🛠️ Prerequisites
- Python 3.10+ installed on your desktop.
- An OpenAI API Key (`sk-proj-...`).
- No complex backend setups required! Only three basic lightweight pip wrapper packages are needed.

## 🚀 Setup & Initialization

### 1. Install Dependencies
Open your terminal or command prompt and install the essential Python libraries:
```bash
pip install openai requests pypdf2
```

### 2. Configure your API Key
To execute the AI orchestration natively, create a `config.json` file in the main project directory possessing your OpenAI key, it should look exactly like this:
```json
{
  "OPENAI_API_KEY": "your-openai-api-key-here",
  "MODEL": "gpt-4o-mini",
  "TEMPERATURE_ANALYSIS": 0.2,
  "TEMPERATURE_GENERATION": 0.7,
  "PORT": 8000
}
```

### 3. Launch the Local Server
Run the python orchestrator file!
```bash
python main.py
```

### 4. Start Optimizing!
Open your web browser and navigate to **[http://localhost:8000](http://localhost:8000)**. 
- **Phase 1:** Upload your static PDF resume to bootstrap your baseline `master_profile.json`. 
- **Phase 2:** Paste in an active job link URL and watch your Tailored Markdown resume map and generate!

---
*Open Source Disclaimer: The root `.gitignore` safely prevents uploading any of your personally identifiable `master_profile.json`, generated tailored resumes, or API keys implicitly ensuring your job-hunting data remains 100% locally secure, even if you fork the repository!*

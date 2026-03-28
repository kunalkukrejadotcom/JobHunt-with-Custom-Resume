import csv
import os
from datetime import datetime

TRACKER_PATH = os.path.join("data", "application_tracker.csv")
APPLICATIONS_DIR = "applications"

def init_tracker():
    os.makedirs(os.path.dirname(TRACKER_PATH), exist_ok=True)
    if not os.path.exists(TRACKER_PATH):
        with open(TRACKER_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Company", "Role", "Job_URL", "Directory_Path", "Pre_Score", "Post_Score", "Status"])

def log_application(company, role, url, directory_path, pre_score, post_score):
    init_tracker()
    date_str = datetime.now().strftime("%Y-%m-%d")
    with open(TRACKER_PATH, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([date_str, company, role, url, directory_path, pre_score, post_score, "Applied"])

def create_application_directory(company, role):
    date_str = datetime.now().strftime("%Y%m%d")
    safe_company = "".join(x for x in company if x.isalnum() or x.isspace()).replace(" ", "")
    safe_role = "".join(x for x in role if x.isalnum() or x.isspace()).replace(" ", "")
    dir_name = f"{safe_company}_{safe_role}_{date_str}"
    dir_path = os.path.join(APPLICATIONS_DIR, dir_name)
    
    counter = 1
    final_dir_path = dir_path
    while os.path.exists(final_dir_path):
        final_dir_path = f"{dir_path}_{counter}"
        counter += 1
        
    os.makedirs(final_dir_path, exist_ok=True)
    return final_dir_path

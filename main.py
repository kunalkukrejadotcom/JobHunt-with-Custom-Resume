import os
import json
import shutil
from http.server import HTTPServer, SimpleHTTPRequestHandler
from core.ingest_resume import bootstrap_master_profile
from core.scraper import scrape_job_description
from core.resume_generator import analyze_job, generate_tailored_resume
from core.tracker import create_application_directory, log_application
from core.llm_client import get_config

PORT = get_config().get("PORT", 8000)

class ResumeBotHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
            
        elif self.path == '/api/user_status':
            try:
                from core.profile_manager import load_profile
                if os.path.exists("data/master_profile.json"):
                    profile = load_profile()
                    name = profile.get("basics", {}).get("name")
                    if name:
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({"exists": True, "name": name.split(" ")[0]}).encode('utf-8'))
                        return
                        
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"exists": False}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
            return
                
        elif self.path == '/api/history':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            history = []
            tracker_path = os.path.join("data", "application_tracker.csv")
            if os.path.exists(tracker_path):
                import csv
                with open(tracker_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    history = list(reader)
            self.wfile.write(json.dumps(history).encode('utf-8'))
            return
            
        return super().do_GET()
        
    def do_POST(self):
        if self.path == '/api/init':
            content_length = int(self.headers['Content-Length'])
            pdf_data = self.rfile.read(content_length)
            
            temp_path = "temp_resume.pdf"
            with open(temp_path, "wb") as f:
                f.write(pdf_data)
            
            print("Processing uploaded resume via OpenAI...")
            try:
                success = bootstrap_master_profile(temp_path)
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": success}).encode("utf-8"))
            except Exception as e:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
        
        elif self.path == '/api/reset':
            try:
                if os.path.exists("data"):
                    shutil.rmtree("data")
                os.makedirs("data", exist_ok=True)
                if os.path.exists("applications"):
                    shutil.rmtree("applications")
                os.makedirs("applications", exist_ok=True)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))

        elif self.path == '/api/analyze_job':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            url = data.get("url")
            
            if not url:
                self.send_error(400, "Missing URL")
                return
                
            try:
                job_markdown = scrape_job_description(url)
                if not job_markdown:
                    raise ValueError("Failed to scrape job description")
                
                job_reqs = analyze_job(job_markdown)
                
                with open("temp_job.md", "w", encoding='utf-8') as f:
                    f.write(job_markdown)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True, 
                    "job_reqs": job_reqs
                }).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

        elif self.path == '/api/generate':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            url = data.get("url")
            job_reqs = data.get("job_reqs")
            confirmed_keywords = data.get("confirmed_keywords", "")
                
            try:
                with open("temp_job.md", "r", encoding='utf-8') as f:
                    job_markdown = f.read()
                    
                company = job_reqs.get("company", "Unknown")
                role = job_reqs.get("role", "Role")
                dir_path = create_application_directory(company, role)
                
                pre_score, post_score, final_md = generate_tailored_resume(url, job_markdown, job_reqs, confirmed_keywords, dir_path)
                
                log_application(company, role, url, dir_path, pre_score, post_score)
                if os.path.exists("temp_job.md"):
                    os.remove("temp_job.md")
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True, 
                    "pre_score": pre_score,
                    "post_score": post_score,
                    "dir_path": dir_path,
                    "resume_md": final_md
                }).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

def run_server():
    os.makedirs("data", exist_ok=True)
    os.makedirs("prompts", exist_ok=True)
    os.makedirs("applications", exist_ok=True)
    
    server_address = ('127.0.0.1', PORT)
    httpd = HTTPServer(server_address, ResumeBotHandler)
    print("==================================================")
    print(f"✅ Resume Optimizer Bot natively running at: http://localhost:{PORT}")
    print("==================================================")
    print("Press Ctrl+C to stop the server.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == '__main__':
    run_server()

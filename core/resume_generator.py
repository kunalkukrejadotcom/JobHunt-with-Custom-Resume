import os
import json
from core.llm_client import get_openai_client, get_config, build_chat_kwargs
from core.profile_manager import load_profile

def load_prompt(filename):
    with open(os.path.join("prompts", filename), 'r', encoding='utf-8') as f:
        return f.read()

def analyze_job(job_markdown):
    """Step 1: Scrape job and extract raw requirements and company data."""
    client = get_openai_client()
    config = get_config()
    print("Extracting job requirements, company, and role...")
    extraction_prompt = load_prompt("job_extraction.txt")
    
    kwargs = build_chat_kwargs(
        config=config,
        messages=[
            {"role": "system", "content": extraction_prompt},
            {"role": "user", "content": f"Job Description:\n{job_markdown}"}
        ],
        temp_key="TEMPERATURE_ANALYSIS",
        response_format={"type": "json_object"}
    )
    resp_extract = client.chat.completions.create(**kwargs)
    job_reqs = json.loads(resp_extract.choices[0].message.content)
    return job_reqs

def evaluate_ats(job_reqs, profile, custom_keywords):
    """Evaluates the FULL Candidate profile JSON against job requirements."""
    client = get_openai_client()
    config = get_config()
    gap_prompt = load_prompt("gap_analysis.txt")
    gap_prompt_hydrated = gap_prompt.replace("{profile_json}", json.dumps(profile)) \
                                    .replace("{job_json}", json.dumps(job_reqs)) \
                                    .replace("{custom_keywords}", custom_keywords or "None")
    
    kwargs = build_chat_kwargs(
        config=config,
        messages=[{"role": "system", "content": gap_prompt_hydrated}],
        temp_key="TEMPERATURE_ANALYSIS",
        response_format={"type": "json_object"}
    )
    resp_gap = client.chat.completions.create(**kwargs)
    return json.loads(resp_gap.choices[0].message.content)

def evaluate_post_ats(job_reqs, resume_markdown, custom_keywords):
    """Evaluates the FINAL Tailored Markdown string against job requirements."""
    client = get_openai_client()
    config = get_config()
    prompt = load_prompt("post_ats_eval.txt")
    prompt_hydrated = prompt.replace("{resume_markdown}", resume_markdown) \
                            .replace("{job_json}", json.dumps(job_reqs)) \
                            .replace("{custom_keywords}", custom_keywords or "None")
    kwargs = build_chat_kwargs(
        config=config,
        messages=[{"role": "system", "content": prompt_hydrated}],
        temp_key="TEMPERATURE_ANALYSIS",
        response_format={"type": "json_object"}
    )
    resp_eval = client.chat.completions.create(**kwargs)
    return json.loads(resp_eval.choices[0].message.content)

def generate_tailored_resume(job_url, job_markdown, job_reqs, custom_keywords, output_dir):
    client = get_openai_client()
    config = get_config()
    profile = load_profile()
    
    # Pre-ATS Score (Current Profile)
    print("Performing pre-tailoring ATS Gap Analysis...")
    pre_gap_analysis = evaluate_ats(job_reqs, profile, custom_keywords)
    pre_match_score = pre_gap_analysis.get("ats_match_score", 0)
    
    # Write Tailored Resume
    print("Generating tailored markdown resume via STAR method...")
    writer_prompt = load_prompt("resume_writer.txt")
    writer_prompt_hydrated = writer_prompt.replace("{selected_experiences_json}", json.dumps(pre_gap_analysis.get("selected_experiences", []))) \
                                          .replace("{profile_basics}", json.dumps(profile.get("basics", {}))) \
                                          .replace("{job_description}", job_markdown) \
                                          .replace("{custom_keywords}", custom_keywords or "None")
    
    kwargs = build_chat_kwargs(
        config=config,
        messages=[{"role": "system", "content": writer_prompt_hydrated}],
        temp_key="TEMPERATURE_GENERATION"
    )
    resp_write = client.chat.completions.create(**kwargs)
    final_resume_md = resp_write.choices[0].message.content
    
    # Clean markdown quotes
    if final_resume_md.startswith("```markdown"):
        final_resume_md = final_resume_md[11:]
    if final_resume_md.startswith("```"):
        final_resume_md = final_resume_md[3:]
    if final_resume_md.endswith("```"):
        final_resume_md = final_resume_md[:-3]
    final_resume_md = final_resume_md.strip()

    # Post-ATS Score (Tailored Resume)
    print("Performing post-tailoring Final ATS Analysis...")
    post_gap_analysis = evaluate_post_ats(job_reqs, final_resume_md, custom_keywords)
    post_match_score = post_gap_analysis.get("ats_match_score", 0)

    # Save Outputs
    with open(os.path.join(output_dir, "job_description.md"), "w", encoding='utf-8') as f:
        f.write(job_markdown)
        
    with open(os.path.join(output_dir, "ats_report_pre.json"), "w", encoding='utf-8') as f:
        json.dump(pre_gap_analysis, f, indent=2)
        
    with open(os.path.join(output_dir, "ats_report_post.json"), "w", encoding='utf-8') as f:
        json.dump(post_gap_analysis, f, indent=2)
        
    with open(os.path.join(output_dir, "tailored_resume.md"), "w", encoding='utf-8') as f:
        f.write(final_resume_md)
        
    return pre_match_score, post_match_score, final_resume_md

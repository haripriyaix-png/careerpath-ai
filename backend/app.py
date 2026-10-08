from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3, json
from pathlib import Path
from recommendation_engine import recommend_careers, skill_gap, generate_roadmap

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / "careerpath.db"
app = Flask(__name__)
CORS(app)

CAREERS = {
    "Cybersecurity Analyst": {
        "description": "Protect systems, investigate security events and monitor threats.",
        "skills": {"cybersecurity":10,"networking":8,"linux":7,"python":6,"siem":9,"incident response":9,"digital forensics":7,"cryptography":5}},
    "Ethical Hacker": {
        "description": "Find and responsibly report vulnerabilities before attackers can exploit them.",
        "skills": {"cybersecurity":10,"linux":8,"networking":8,"python":7,"web security":9,"penetration testing":10,"cryptography":5}},
    "Software Developer": {
        "description": "Design, build, test and maintain software applications.",
        "skills": {"python":7,"java":7,"c++":6,"javascript":8,"sql":6,"problem solving":8,"git":6}},
    "Data Scientist": {
        "description": "Use data, statistics and machine learning to solve problems.",
        "skills": {"python":8,"sql":8,"data analysis":9,"statistics":8,"machine learning":9,"communication":5}},
    "Machine Learning Engineer": {
        "description": "Build, deploy and maintain machine-learning systems.",
        "skills": {"python":9,"machine learning":10,"data analysis":8,"statistics":7,"sql":6,"cloud computing":6}},
    "Cloud Engineer": {
        "description": "Build and operate reliable cloud infrastructure and services.",
        "skills": {"cloud computing":10,"linux":8,"networking":8,"python":6,"devops":8,"security":6}},
    "DevOps Engineer": {
        "description": "Automate software delivery, infrastructure and operational workflows.",
        "skills": {"linux":8,"cloud computing":9,"devops":10,"python":7,"git":8,"networking":6}},
    "Network Engineer": {
        "description": "Design, configure and troubleshoot computer networks.",
        "skills": {"networking":10,"linux":6,"cybersecurity":6,"cloud computing":5,"problem solving":7}}
}

RESOURCES = [
    {"title":"Linux Fundamentals","platform":"Cisco Networking Academy","type":"Free","skill":"Linux","duration":"20 hours"},
    {"title":"Introduction to Cybersecurity","platform":"Cisco Networking Academy","type":"Free","skill":"Cybersecurity","duration":"15 hours"},
    {"title":"Python for Everybody","platform":"Coursera","type":"Free to audit","skill":"Python","duration":"30 hours"},
    {"title":"Web Security Academy","platform":"PortSwigger","type":"Free","skill":"Web Security","duration":"Self-paced"},
    {"title":"Cybersecurity Career Path","platform":"TryHackMe","type":"Free / Paid","skill":"Cybersecurity","duration":"Self-paced"},
    {"title":"Security+ Preparation","platform":"CompTIA","type":"Certification","skill":"Security Fundamentals","duration":"60+ hours"}
]

PROJECTS = [
    {"title":"Password Strength Analyzer","difficulty":"Beginner","hours":6,"skills":["Python","Security"],"description":"Build a local educational tool that evaluates password strength."},
    {"title":"Network Scanner","difficulty":"Intermediate","hours":12,"skills":["Python","Networking"],"description":"Create a controlled local-network scanner for learning network discovery."},
    {"title":"Log Analysis Dashboard","difficulty":"Intermediate","hours":18,"skills":["Python","SIEM","Data Analysis"],"description":"Parse sample security logs and visualize suspicious patterns."},
    {"title":"Phishing Awareness Simulator","difficulty":"Intermediate","hours":16,"skills":["Web Security","Cybersecurity"],"description":"Build an educational simulator using mock data to teach phishing detection."}
]

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS profiles (
      id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, degree TEXT, branch TEXT,
      college TEXT, year TEXT, level TEXT, career_goal TEXT, target_salary TEXT,
      work_type TEXT, interests TEXT, skills_json TEXT
    );
    CREATE TABLE IF NOT EXISTS feedback (
      id INTEGER PRIMARY KEY AUTOINCREMENT, profile_id INTEGER, rating INTEGER,
      relevance INTEGER, usefulness INTEGER, achievability INTEGER, comment TEXT
    );
    CREATE TABLE IF NOT EXISTS roadmap_progress (
      profile_id INTEGER, item_id TEXT, completed INTEGER DEFAULT 0,
      PRIMARY KEY(profile_id, item_id)
    );
    """)
    conn.commit()
    conn.close()

@app.get("/api/health")
def health():
    return jsonify({"ok": True, "service": "CareerPath AI API"})

@app.get("/api/careers")
def careers():
    return jsonify([{"name":n,"description":d["description"],"skills":list(d["skills"])} for n,d in CAREERS.items()])

@app.post("/api/profile")
def save_profile():
    data = request.get_json(force=True)
    conn = db()
    cur = conn.execute("""INSERT INTO profiles
      (name,degree,branch,college,year,level,career_goal,target_salary,work_type,interests,skills_json)
      VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
      (data.get("name"),data.get("degree"),data.get("branch"),data.get("college"),data.get("year"),
       data.get("level"),data.get("career_goal"),data.get("target_salary"),data.get("work_type"),
       json.dumps(data.get("interests",[])),json.dumps(data.get("skills",[]))))
    conn.commit()
    pid = cur.lastrowid
    conn.close()
    return jsonify({"id":pid,"profile":data})

@app.post("/api/recommend-careers")
def recommend():
    return jsonify({"recommendations": recommend_careers(request.get_json(force=True), CAREERS)})

@app.post("/api/skill-gap")
def gaps():
    data = request.get_json(force=True)
    return jsonify(skill_gap(data, data.get("career_goal") or "Cybersecurity Analyst", CAREERS))

@app.post("/api/generate-roadmap")
def roadmap():
    data = request.get_json(force=True)
    career = data.get("career_goal") or "Cybersecurity Analyst"
    return jsonify({"career":career,"roadmap":generate_roadmap(data,career,CAREERS)})

@app.get("/api/resources")
def resources():
    return jsonify(RESOURCES)

@app.get("/api/projects")
def projects():
    return jsonify(PROJECTS)

@app.post("/api/feedback")
def feedback():
    data = request.get_json(force=True)
    conn = db()
    conn.execute("""INSERT INTO feedback
      (profile_id,rating,relevance,usefulness,achievability,comment) VALUES (?,?,?,?,?,?)""",
      (data.get("profile_id"),data.get("rating",5),data.get("relevance",5),
       data.get("usefulness",5),data.get("achievability",5),data.get("comment","")))
    conn.commit()
    conn.close()
    return jsonify({"saved":True,"message":"Feedback saved"})

@app.post("/api/roadmap/progress")
def progress():
    data = request.get_json(force=True)
    conn = db()
    conn.execute("""INSERT INTO roadmap_progress(profile_id,item_id,completed) VALUES(?,?,?)
      ON CONFLICT(profile_id,item_id) DO UPDATE SET completed=excluded.completed""",
      (data.get("profile_id",0),data.get("item_id"),int(bool(data.get("completed")))))
    conn.commit()
    conn.close()
    return jsonify({"saved":True})

init_db()
if __name__ == "__main__":
    app.run(debug=True, port=5000)

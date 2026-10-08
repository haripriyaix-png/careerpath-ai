def normalize(value):
    return str(value).strip().lower()

def skill_map(profile):
    result = {}
    for item in profile.get("skills", []):
        if isinstance(item, str):
            result[normalize(item)] = 0.65
        else:
            name = normalize(item.get("name", ""))
            level = normalize(item.get("level", "beginner"))
            weight = {"beginner": 0.4, "intermediate": 0.7, "advanced": 1.0}.get(level, 0.4)
            if name:
                result[name] = weight
    return result

def recommend_careers(profile, careers):
    student_skills = skill_map(profile)
    interests = {normalize(x) for x in profile.get("interests", [])}
    goal = normalize(profile.get("career_goal", ""))
    results = []
    for name, career in careers.items():
        required = career["skills"]
        earned = 0
        total = sum(required.values())
        matched, missing = [], []
        for skill, weight in required.items():
            s = normalize(skill)
            if s in student_skills:
                earned += weight * student_skills[s]
                matched.append(skill)
            else:
                missing.append(skill)
        interest_bonus = sum(3 for interest in interests if interest in required or interest in name.lower())
        goal_bonus = 7 if goal and goal == normalize(name) else 0
        score = min(98, round((earned / total) * 100 + interest_bonus + goal_bonus))
        results.append({
            "career": name, "match": max(35, score),
            "description": career["description"],
            "matched": matched[:5], "missing": missing[:5]
        })
    return sorted(results, key=lambda x: x["match"], reverse=True)

def skill_gap(profile, career, careers):
    if career not in careers:
        career = "Cybersecurity Analyst"
    student = skill_map(profile)
    rows = []
    for skill, importance in careers[career]["skills"].items():
        current = round(student.get(normalize(skill), 0) * 100)
        required = min(100, importance * 10)
        gap = max(0, required - current)
        rows.append({
            "skill": skill.title(), "current": current, "required": required,
            "gap": gap,
            "priority": "High" if gap >= 50 else "Medium" if gap >= 25 else "Low"
        })
    rows.sort(key=lambda x: x["gap"], reverse=True)
    return {"career": career, "skills": rows, "priority": rows[:3]}

def generate_roadmap(profile, career, careers):
    gaps = skill_gap(profile, career, careers)["skills"]
    missing = [x["skill"] for x in gaps if x["gap"] > 15][:8]
    groups = [
        ("Month 1", "Foundation", ["Linux Basics", "Networking Fundamentals", "Python for Security"]),
        ("Month 2", "Core Skills", missing[:3] or ["Security Fundamentals", "OWASP Basics", "Cryptography"]),
        ("Month 3", "Practical Skills", ["Wireshark", "SIEM Fundamentals", "Vulnerability Assessment"]),
        ("Month 4", "Projects", ["Network Scanner", "Log Analysis Dashboard"]),
        ("Month 5", "Certification", ["Security+ Preparation"]),
        ("Month 6", "Career Preparation", ["GitHub Portfolio", "Resume and Mock Interview"])
    ]
    roadmap, counter = [], 1
    for month, phase, items in groups:
        for item in items:
            roadmap.append({
                "id": f"r{counter}", "month": month, "phase": phase,
                "title": item,
                "description": f"Build practical ability in {item.lower()} as part of the {career} path.",
                "difficulty": "Beginner" if counter <= 3 else "Intermediate",
                "hours": 8 + (counter % 4) * 3, "status": "upcoming"
            })
            counter += 1
    return roadmap

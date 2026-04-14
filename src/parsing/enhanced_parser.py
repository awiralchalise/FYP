import re
from typing import Dict, List
from .text_cleaner import clean_skill_list
from .pdf_table_extractor import extract_skills_from_pdf_tables

def enhanced_extract_sections(text: str, file_path: str = None) -> Dict[str, List[str]]:
    """
    Enhanced section extraction that works for ALL resume types
    """
    sections = {
        "skills": [],
        "education": [],
        "experience": [],
        "certifications": []
    }
    
    # STRATEGY 1: Direct table extraction for PDFs
    table_skills = []
    if file_path and file_path.lower().endswith('.pdf'):
        try:
            table_skills = extract_skills_from_pdf_tables(file_path)
            sections["skills"].extend(table_skills)
            print(f"DEBUG: Table extraction found {len(table_skills)} skills")
        except Exception as e:
            print(f"Table extraction failed: {e}")
    
    # STRATEGY 2: Use your PROVEN regex patterns (they work!)
    section_patterns = {
        "skills": [
            r"^\s*(?:skills?/core\s+competencies|skills?|technical\s+skills?|technologies|expertise|competencies|core\s+competencies|proficiencies)\b[:\-\s]*(.*?)(?=^\s*(?:education|experience|work|projects|certifications|career)\b|\Z)",
            r"^\s*skills?/core\s+competencies\b[:\-\s]*(.*?)(?=^\s*(?:education|experience|work|projects|certifications|career)\b|\Z)"
        ],
        
        "education": [
            r"^\s*(?:education|academic\s+background|qualifications|academics|degrees?)\b[:\-\s]*(.*?)(?=^\s*(?:experience|skills|work|projects|certifications|career)\b|\Z)",
            r"^\s*education\b[:\-\s]*(.*?)(?=^\s*(?:experience|skills|work|projects|certifications|career)\b|\Z)"
        ],
        
        "experience": [
            r"^\s*(?:experience|work\s+history|employment|professional(?:\s+experience)?|career\s+history|work\s+experience)\b[:\-\s]*(.*?)(?=^\s*(?:education|skills|projects|certifications|teaching|trainings)\b|\Z)",
            r"^\s*career\s+history\b[:\-\s]*(.*?)(?=^\s*(?:education|skills|projects|certifications|teaching|trainings)\b|\Z)"
        ],
        
        "certifications": [
            r"^\s*(?:certifications?|certificates?|qualifications|licenses?)\b[:\-\s]*(.*?)(?=^\s*(?:education|experience|skills|basic\s+information)\b|\Z)",
            r"^\s*certifications\b[:\-\s]*(.*?)(?=^\s*(?:education|experience|skills|basic\s+information)\b|\Z)"
        ]
    }
    
    # Try each pattern for each section
    for section, patterns in section_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL | re.MULTILINE)
            if match:
                content = match.group(1).strip()
                print(f"DEBUG: Found {section} section using pattern")
                
                if section == "skills":
                    items = split_skills_string(content)
                else:
                    items = [item.strip() for item in re.split(r'[\n•\-]', content) if item.strip()]
                
                sections[section].extend(items)
                break  # Use first matching pattern
    
    # STRATEGY 3: Fallback extraction for sections not found by regex
    if not sections["skills"]:
        skills_fallback = extract_section_fallback(text, "skills")
        sections["skills"].extend(skills_fallback)
    
    if not sections["education"]:
        education_fallback = extract_section_fallback(text, "education")
        sections["education"].extend(education_fallback)
    
    if not sections["experience"]:
        experience_fallback = extract_section_fallback(text, "experience")
        sections["experience"].extend(experience_fallback)

    # STRATEGY 4: Extract skills from entire text using keyword scanning
    if len(sections["skills"]) < 4:  # If few skills found
        text_skills = extract_skills_from_text_keywords(text)
        sections["skills"].extend(text_skills)
        print(f"DEBUG: Keyword extraction found {len(text_skills)} skills")
    
    # Clean and deduplicate skills
    if sections["skills"]:
        sections["skills"] = clean_skill_list(sections["skills"])
        print(f"🎯 Final skills after cleaning: {len(sections['skills'])} skills")
    
    return sections 

def extract_section_fallback(text: str, section: str) -> List[str]:
    """Robust fallback method for various section headers"""
    section_patterns = {
        "skills": [
            r"^\s*Skills/Core Competencies\b[:\-\s]*(.*?)(?=^\s*(?:Education|Experience|Certifications|Work)\b|\Z)",
            r"^\s*Technical Skills?\b[:\-\s]*(.*?)(?=^\s*(?:Education|Experience|Work)\b|\Z)",
            r"^\s*Skills?\b[:\-\s]*(.*?)(?=^\s*(?:Education|Experience|Work)\b|\Z)"
        ],
        "education": [
            r"^\s*Education\b[:\-\s]*(.*?)(?=^\s*(?:Skills|Experience|Work)\b|\Z)",
            r"^\s*Academic Background\b[:\-\s]*(.*?)(?=^\s*(?:Skills|Experience|Work)\b|\Z)",
            r"^\s*Qualifications?\b[:\-\s]*(.*?)(?=^\s*(?:Skills|Experience|Work)\b|\Z)"
        ],
        "experience": [
            r"^\s*Career history\b[:\-\s]*(.*?)(?=^\s*(?:Education|Skills|Teaching)\b|\Z)",
            r"^\s*Work Experience\b[:\-\s]*(.*?)(?=^\s*(?:Education|Skills)\b|\Z)",
            r"^\s*Professional Experience\b[:\-\s]*(.*?)(?=^\s*(?:Education|Skills)\b|\Z)",
            r"^\s*Employment\b[:\-\s]*(.*?)(?=^\s*(?:Education|Skills)\b|\Z)"
        ]
    }
    
    if section in section_patterns:
        for pattern in section_patterns[section]:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL | re.MULTILINE)
            if match:
                content = match.group(1).strip()
                print(f"DEBUG: Fallback found {section} section with pattern: {pattern[:50]}...")
                
                if section == "skills":
                    return split_skills_string(content)
                else:
                    return [item.strip() for item in re.split(r'[\n•\-]', content) if item.strip()]
    
    return []


def parse_education_section(content: str) -> List[str]:
    """Parse education section focusing on degree information"""
    items = []
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    current_item = ""
    for line in lines:
        # Look for degree patterns
        if re.search(r'(?:bachelor|master|msc?|bsc?|phd|degree|diploma|certificate|\.\d{4}|\d{4}\s*\-)', line, re.I):
            if current_item:
                items.append(current_item.strip())
            current_item = line
        elif current_item and line and len(line) < 100:
            current_item += " " + line
        elif line and len(line) < 150:  # Reasonable length for education items
            items.append(line)
    
    if current_item:
        items.append(current_item.strip())
    
    return items if items else [item.strip() for item in re.split(r'[\n•\-]', content) if item.strip() and len(item.strip()) < 200] 


def extract_skills_from_text_keywords(text: str) -> List[str]:
    """Extract skills by scanning entire text for keywords"""
    skills_found = set()
    
    # Common technical skills
    technical_skills = [
        'cyber security', 'ethical hacking', 'penetration testing', 'vulnerability assessments',
        'security risk assessment', 'server hardening', 'application hardening', 'security baseline configuration',
        'is audit', 'information security', 'data protection', 'vapt', 'risk analysis',
        # Programming Languages
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 'swift', 'kotlin',
        'r', 'scala', 'rust', 'matlab', 'perl', 'bash', 'shell', 'powershell',
        
        # Data Science & ML
        'machine learning', 'deep learning', 'artificial intelligence', 'ai', 'data science', 'data analysis',
        'data visualization', 'statistical analysis', 'predictive modeling', 'regression', 'classification',
        'clustering', 'natural language processing', 'nlp', 'computer vision', 'neural networks', 'time series',
        'a/b testing', 'hypothesis testing', 'exploratory data analysis', 'eda', 'feature engineering',
        'model selection', 'cross validation', 'hyperparameter tuning', 'ensemble methods',
        # Data Tools
        'pandas', 'numpy', 'scipy', 'scikit-learn', 'sklearn', 'tensorflow', 'pytorch', 'keras', 'mxnet',
        'matplotlib', 'seaborn', 'plotly', 'bokeh', 'd3.js', 'ggplot2', 'tableau', 'power bi', 'powerbi',
        'qlik', 'looker', 'jupyter', 'google colab', 'rstudio', 'spss', 'sas', 'stata',
        
        # Databases
        'sql', 'mysql', 'postgresql', 'postgres', 'oracle', 'sql server', 'mongodb', 'redis', 'couchbase',
        'dynamodb', 'cassandra', 'neo4j', 'sqlite', 'firebase', 'cosmos db', 'bigquery', 'snowflake',
        
        # Big Data
        'spark', 'pyspark', 'hadoop', 'hive', 'kafka', 'storm', 'flink', 'beam', 'airflow', 'luigi',
        'presto', 'hbase', 'cassandra', 'elasticsearch', 'splunk',
        # Cloud & DevOps
        'aws', 'amazon web services', 'azure', 'microsoft azure', 'gcp', 'google cloud', 'docker', 'kubernetes',
        'jenkins', 'git', 'github', 'gitlab', 'bitbucket', 'terraform', 'ansible', 'puppet', 'chef',
        'ci/cd', 'continuous integration', 'continuous deployment', 'devops', 'mlops',
        
        # Web Development
        'html', 'css', 'react', 'angular', 'vue', 'node', 'node.js', 'express', 'django', 'flask', 'spring',
        'laravel', 'ruby on rails', 'asp.net', 'php', 'wordpress', 'drupal', 'joomla',
        
        # Mobile Development
        'android', 'ios', 'swift', 'react native', 'flutter', 'xamarin', 'ionic', 'cordova',
        
        # Tools & Software
        'excel', 'powerpoint', 'word', 'outlook', 'sharepoint', 'jira', 'confluence', 'slack', 'teams',
        'zoom', 'photoshop', 'illustrator', 'figma', 'sketch', 'invision',
        'adobe xd', 'canva', 'notion', 'evernote',
        # Methodologies
        'agile', 'scrum', 'kanban', 'waterfall', 'lean', 'six sigma', 'devops',
        
        # Soft Skills
        'communication', 'problem solving', 'teamwork', 'leadership', 'project management', 'time management',
        'critical thinking', 'analytical skills', 'creativity', 'adaptability', 'presentation', 'negotiation'
    ]
    
    text_lower = text.lower()
    
    for skill in technical_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            skills_found.add(skill)
    
    return list(skills_found)

# KEEP YOUR EXISTING helper functions
def split_skills_string(skills_text: str) -> List[str]:
    if not skills_text:
        return []
    
    print(f"DEBUG: split_skills_string input: {skills_text[:200]}...")
    
    # FIRST: Try to extract bullet points with multi-word skills
    lines = [line.strip() for line in skills_text.split('\n') if line.strip()]
    
    bullet_skills = []
    for line in lines:
        # Skip lines that are too long (paragraphs)
        if len(line) > 80:
            continue
            
        # Remove ALL types of bullets including ▪ 
        clean_line = re.sub(r'^[\-\•\*\–\—\▪]\s*', '', line)
        
        # Check if this looks like a skill (not a sentence, not too long)
        if (len(clean_line) <= 50 and 
            not re.search(r'[.!?]\s*[A-Z]', clean_line) and  # Not a sentence
            not clean_line.endswith('.') and  # Not ending with period
            clean_line and not clean_line.isdigit() and
            len(clean_line) > 2):  # At least 3 characters
            
            skill = clean_line.strip()
            if skill:
                bullet_skills.append(skill)
    
    # If we found good bullet skills, use them
    if bullet_skills:
        print(f"DEBUG: Found {len(bullet_skills)} bullet skills: {bullet_skills}")
        return bullet_skills
    
    # SECOND: If no bullets found, use SIMPLE space-based splitting but preserve multi-word
    skills = []
    lines = [line.strip() for line in skills_text.split('\n') if line.strip()]
    
    for line in lines:
        # Remove bullets
        clean_line = re.sub(r'^[\-\•\*\–\—\▪]\s*', '', line)
        
        # If line is short and looks like skills, use the whole line
        if len(clean_line) <= 50 and len(clean_line) > 2:
            skills.append(clean_line)
        else:
            # Fallback to your original delimiter approach
            delimiters = [',', ';', '/', '|', '&']
            for delimiter in delimiters:
                if delimiter in clean_line:
                    parts = clean_line.split(delimiter)
                    for part in parts:
                        skill = part.strip()
                        if skill and len(skill) > 2 and not skill.isdigit():
                            skills.append(skill)
                    break
            else:
                # If no delimiters, try to preserve multi-word skills
                # Look for patterns like "Cyber Security", "Ethical Hacking"
                potential_skills = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+|[A-Z][a-z]+', clean_line)
                for skill in potential_skills:
                    if len(skill) > 2 and len(skill) <= 30:
                        skills.append(skill)
    
    # Clean up the skills
    cleaned_skills = []
    for skill in skills:
        skill = re.sub(r'^\W+|\W+$', '', skill)  # Remove surrounding punctuation
        if skill and len(skill) > 2:
            cleaned_skills.append(skill)
    
    print(f"DEBUG: Final skills from split_skills_string: {cleaned_skills}")
    return cleaned_skills

def split_skills_by_uppercase(text: str) -> List[str]:
    skills = re.findall(r'[A-Z][a-z]+|[A-Z]+(?=[A-Z]|$)', text)
    return [skill.strip() for skill in skills if skill.strip()]


def _normalize_resume_line(line: str) -> str:
    line = line.replace('\xa0', ' ')
    line = re.sub(r'\s+', ' ', line)
    # Repair common PDF extraction splits inside words/technologies.
    replacements = {
        "Commun Ication": "Communication",
        "Commun ication": "Communication",
        "Dot Ne T": ".NET",
        "Dot Net": ".NET",
        "React Native Dot Net": "React Native .NET",
        "Intermedia Te": "Intermediate",
        "Intermedia te": "Intermediate",
        "Writ Ten": "Written",
        "Writ ten": "Written",
        "Oral Commun Ication": "Oral Communication",
        "Technical S Kills": "Technical Skills",
        "Proficiency Intermedia Te": "Proficiency Intermediate",
        "Competency Advanced": "Competency Advanced",
        "Swift Objective c": "Swift Objective-C",
        "Objective c": "Objective-C",
        "New York University of Technology": "New York University of Technology",
    }
    for bad, good in replacements.items():
        line = line.replace(bad, good)

    # Merge obvious PDF-fractured words like "Commun ication" or "s kill".
    merge_patterns = [
        (r'\b([A-Z][a-z]{4,})\s([A-Z][a-z]{1,2})\b', r'\1\2'),
        (r'\b([A-Z][a-z]{1,2})\s([A-Z][a-z]{4,})\b', r'\1\2'),
    ]
    previous = None
    while line != previous:
        previous = line
        for pattern, replacement in merge_patterns:
            line = re.sub(pattern, replacement, line)

    # Restore spacing when the generic repair is too aggressive around known phrases.
    line = re.sub(r'\b(React)\s*(Native)\b', r'\1 \2', line, flags=re.IGNORECASE)
    line = re.sub(r'\b(Technical)\s*(Skills)\b', r'\1 \2', line, flags=re.IGNORECASE)
    line = re.sub(r'\b(Oral)\s*(Communication)\b', r'\1 \2', line, flags=re.IGNORECASE)
    line = re.sub(r'\b(Written)\s*(And)\s*(Oral)\b', r'\1 And \3', line, flags=re.IGNORECASE)
    line = re.sub(r'\b(Advanced)\s*(English)\b', r'\1 \2', line, flags=re.IGNORECASE)
    line = re.sub(r'\b(Intermediate)\s*(Nepali)\b', r'\1 \2', line, flags=re.IGNORECASE)
    return line.strip()


def _split_compound_skill_phrase(text: str) -> List[str]:
    """Break long skill phrases that were collapsed by PDF extraction."""
    phrase = _normalize_resume_line(text)
    if not phrase:
        return []

    scan_phrase = phrase
    detected: List[str] = []
    compound_patterns = [
        (r'Written\s+And\s+Oral\s+Communication', 'Written and Oral Communication'),
        (r'Technical\s+Skills', 'Technical Skills'),
        (r'React\s+Native', 'React Native'),
        (r'(?<!Native\s)React\b', 'React'),
        (r'(?:\.NET|Dot\s+Net)', '.NET'),
        (r'Advanced\s+English', 'Advanced English'),
        (r'(?:Intermediate\s+Nepali|Nepali\s+.*Intermediate)', 'Intermediate Nepali'),
        (r'\bCommunication\b', 'Communication'),
    ]
    for pattern, label in compound_patterns:
        if re.search(pattern, scan_phrase, re.IGNORECASE):
            detected.append(label)
            scan_phrase = re.sub(pattern, ' ', scan_phrase, count=1, flags=re.IGNORECASE)

    remaining = re.sub(r'[\W_]+', '', scan_phrase)
    if len(detected) >= 2 or (detected and len(remaining) <= 5):
        return detected

    phrase = phrase.replace("Written And Oral Communication", "Written and Oral Communication")
    phrase = phrase.replace("React React Native .NET", "React, React Native, .NET")
    phrase = phrase.replace("Communication React", "Communication, React")
    phrase = phrase.replace("Advanced English Nepali", "Advanced English, Nepali")
    phrase = phrase.replace("Nepali Intermediate", "Intermediate Nepali")
    phrase = re.sub(r'\b(Competency|Competencies|Proficiency|Languages?)\b', ', ', phrase, flags=re.IGNORECASE)

    markers = [
        "Technical Skills",
        "React Native",
        "React",
        ".NET",
        "Advanced English",
        "Intermediate Nepali",
        "Communication",
    ]

    for marker in markers:
        escaped = re.escape(marker)
        phrase = re.sub(rf'(?<!^)\s+(?={escaped}\b)', ', ', phrase, flags=re.IGNORECASE)

    parts = [_normalize_resume_line(part).strip(' ,') for part in phrase.split(',')]
    return [part for part in parts if part]


def _split_plain_section(content: str) -> List[str]:
    return [
        _normalize_resume_line(item)
        for item in re.split(r'[\nâ€¢]', content)
        if _normalize_resume_line(item)
    ]


def _parse_education_entries(content: str) -> List[str]:
    lines = [_normalize_resume_line(line) for line in content.split('\n')]
    lines = [line for line in lines if line]

    items: List[str] = []
    current = ""

    for line in lines:
        if any(noise in line.lower() for noise in ["copyright of qwikresume", "usage", "guidelines"]):
            continue
        if re.search(r'(bachelor|master|msc|bsc|phd|degree|diploma|certificate|university|college|school)', line, re.IGNORECASE):
            if current:
                items.append(current.strip())
            current = line
        elif current:
            current += f" {line}"

    if current:
        items.append(current.strip())

    cleaned = []
    for item in items:
        item = re.sub(r'\s+', ' ', item).strip(' -')
        if item and 'copyright of qwikresume' not in item.lower():
            cleaned.append(item)
    return cleaned


def _looks_like_experience_header(line: str, raw_line: str, next_line: str = "") -> bool:
    primary_bullet = bool(re.match(r'^[•\-\*]\s*', raw_line))
    has_date = bool(re.search(r'(?:19|20)\d{2}|present|till now|till|current', line, re.IGNORECASE))
    role_word = bool(re.search(r'\b(manager|engineer|analyst|developer|scientist|director|officer|administrator|lecturer|assistant|intern|consultant|lead|specialist)\b', line, re.IGNORECASE))
    org_word = bool(re.search(r'\b(at|from)\b', line, re.IGNORECASE))
    short_role_title = len(line) <= 60 and role_word and bool(re.search(r'(?:19|20)\d{2}|present|till now|till|current', next_line, re.IGNORECASE))
    return primary_bullet or short_role_title or (has_date and (role_word or org_word))


def _parse_experience_entries(content: str) -> List[str]:
    raw_lines = [line for line in content.split('\n') if line.strip()]
    entries: List[str] = []
    current = ""

    for idx, raw_line in enumerate(raw_lines):
        normalized = _normalize_resume_line(raw_line)
        if not normalized:
            continue

        clean_line = re.sub(r'^[•\-\*o▪◦]+\s*', '', normalized).strip()
        is_sub_bullet = bool(re.match(r'^[o▪◦]\s+', raw_line.strip(), re.IGNORECASE))

        if _looks_like_experience_header(clean_line, raw_line.strip()):
            if current:
                entries.append(current.strip())
            current = clean_line
        elif is_sub_bullet and current:
            current += f" {clean_line}"
        elif current:
            current += f" {clean_line}"
        else:
            current = clean_line

    if current:
        entries.append(current.strip())

    cleaned = []
    for entry in entries:
        entry = re.sub(r'\s+', ' ', entry).strip(' -')
        if entry:
            cleaned.append(entry)
    return cleaned


def _extract_first_section(text: str, patterns: List[str]) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL | re.MULTILINE)
        if match:
            return match.group(1).strip()
    return ""


def _normalize_section_boundaries(text: str) -> str:
    """Insert section-friendly line breaks for PDFs that collapse headings inline."""
    normalized = text.replace('\r\n', '\n').replace('\r', '\n')
    normalized = re.sub(r'[ \t]+', ' ', normalized)

    inline_headings = [
        "Technical Skills",
        "Core Competencies",
        "Work Experience",
        "Professional Experience",
        "Career history",
        "Academic Background",
        "Basic Information",
    ]

    standalone_headings = [
        "Certifications",
        "Qualifications",
        "Experience",
        "Education",
        "Projects",
        "Summary",
        "Objective",
        "Skills",
        "Languages",
        "Trainings",
        "Teaching",
    ]

    for heading in inline_headings:
        escaped = re.escape(heading)
        normalized = re.sub(
            rf'(?<=[a-z0-9\.\)])({escaped})\b',
            rf'\n\1',
            normalized,
            flags=re.IGNORECASE,
        )

    for heading in inline_headings + standalone_headings:
        escaped = re.escape(heading)
        normalized = re.sub(
            rf'\b({escaped})\b\s+(?=(?-i:[A-Z]))',
            rf'\1\n',
            normalized,
            flags=re.IGNORECASE,
        )

    normalized = re.sub(r'\n{3,}', '\n\n', normalized)
    return normalized


def enhanced_extract_sections(text: str, file_path: str = None) -> Dict[str, List[str]]:
    """
    Cleaner section extraction that prefers real headings and keeps multi-line
    experience entries grouped together.
    """
    sections = {
        "skills": [],
        "education": [],
        "experience": [],
        "certifications": []
    }

    normalized_text = _normalize_section_boundaries(text)

    if file_path and file_path.lower().endswith('.pdf'):
        try:
            table_skills = extract_skills_from_pdf_tables(file_path)
            sections["skills"].extend(table_skills)
        except Exception:
            pass

    section_patterns = {
        "skills": [
            r"^\s*(?:skills?/core\s+competencies|skills?|technical\s+skills?|technologies|expertise|competencies|core\s+competencies|proficiencies)\b[:\-\s]*(.*?)(?=^\s*(?:education|experience|work|projects|certifications|career|teaching|trainings)\b|\Z)",
        ],
        "education": [
            r"^\s*(?:education|academic\s+background|qualifications|academics|degrees?)\b[:\-\s]*(.*?)(?=^\s*(?:experience|skills|work|projects|certifications|career|teaching|trainings)\b|\Z)",
        ],
        "experience": [
            r"^\s*(?:experience|work\s+history|employment|professional(?:\s+experience)?|career\s+history|work\s+experience)\b[:\-\s]*(.*?)(?=^\s*(?:education|skills|projects|certifications|teaching|trainings)\b|\Z)",
        ],
        "certifications": [
            r"^\s*(?:certifications?|certificates?|licenses?)\b[:\-\s]*(.*?)(?=^\s*(?:education|experience|skills|projects)\b|\Z)",
        ],
    }

    skills_content = _extract_first_section(normalized_text, section_patterns["skills"])
    education_content = _extract_first_section(normalized_text, section_patterns["education"])
    experience_content = _extract_first_section(normalized_text, section_patterns["experience"])
    cert_content = _extract_first_section(normalized_text, section_patterns["certifications"])

    if skills_content:
        sections["skills"].extend(split_skills_string(skills_content))
    if education_content:
        sections["education"].extend(_parse_education_entries(education_content))
    if experience_content:
        sections["experience"].extend(_parse_experience_entries(experience_content))
    if cert_content:
        sections["certifications"].extend(_split_plain_section(cert_content))

    if len(sections["skills"]) < 4:
        sections["skills"].extend(extract_skills_from_text_keywords(normalized_text))

    if sections["skills"]:
        sections["skills"] = clean_skill_list(sections["skills"])

    return sections


def split_skills_string(skills_text: str) -> List[str]:
    """Cleaner skill splitting for comma-heavy and bullet-heavy resumes."""
    if not skills_text:
        return []

    lines = [_normalize_resume_line(line) for line in skills_text.split('\n') if _normalize_resume_line(line)]
    bullet_skills: List[str] = []

    for line in lines:
        clean_line = re.sub(r'^[^\w]+', '', line).strip()
        if clean_line.lower() in {"skills", "core competencies", "/ core competencies"}:
            continue
        if len(clean_line) <= 60 and not clean_line.endswith('.') and not re.search(r'[.!?]\s+[A-Z]', clean_line):
            if any(bad in clean_line.lower() for bad in ["project description", "project details", "summary", "education", "experience"]):
                continue
            bullet_skills.append(clean_line)

    if bullet_skills:
        return bullet_skills

    skills: List[str] = []
    for line in lines:
        clean_line = re.sub(r'^[^\w]+', '', line).strip()
        if not clean_line or clean_line.lower() in {"skills", "core competencies", "/ core competencies"}:
            continue

        if any(d in clean_line for d in [',', ';', '|', '&', '/']):
            for part in re.split(r'[,;|/&]', clean_line):
                expanded_parts = _split_compound_skill_phrase(part)
                if not expanded_parts:
                    expanded_parts = [_normalize_resume_line(part).strip('.')]
                for skill in expanded_parts:
                    if skill and (len(skill) > 2 or skill.upper() in {"R", "C", "C#", "C++"}):
                        skills.append(skill)
            continue

        if len(clean_line) <= 50 and len(clean_line) > 2:
            skills.append(clean_line)
        elif len(clean_line) > 50:
            for skill in _split_compound_skill_phrase(clean_line):
                if skill and (len(skill) > 2 or skill.upper() in {"R", "C", "C#", "C++"}):
                    skills.append(skill)

    cleaned = []
    special_skills = {"C#", "C++", ".NET"}
    for skill in skills:
        if skill in special_skills:
            cleaned.append(skill)
            continue
        skill = re.sub(r'^\W+|\W+$', '', skill)
        if skill and (len(skill) > 2 or skill.upper() in {"R", "C", "C#", "C++"}):
            cleaned.append(skill)
    return cleaned


def _parse_education_entries_v2(content: str) -> List[str]:
    lines = [_normalize_resume_line(line) for line in content.split('\n')]
    lines = [line for line in lines if line]

    items: List[str] = []
    current = ""
    degree_pattern = r'(bachelor|master|msc|bsc|phd|degree|diploma|certificate|university|college|school|secondary education|higher secondary)'

    for line in lines:
        lowered = line.lower()
        if any(noise in lowered for noise in ["copyright of qwikresume", "usage", "guidelines"]):
            continue

        if re.search(degree_pattern, line, re.IGNORECASE):
            if current:
                items.append(current.strip())
            current = line
        elif current:
            current += f" {line}"

    if current:
        items.append(current.strip())

    return [re.sub(r'\s+', ' ', item).strip(' -') for item in items if item.strip()]


def _looks_like_experience_header_v2(line: str, raw_line: str, next_line: str = "") -> bool:
    has_date = bool(re.search(r'(?:19|20)\d{2}|present|till now|till|current', line, re.IGNORECASE))
    role_word = bool(re.search(r'\b(manager|engineer|analyst|developer|scientist|director|officer|administrator|lecturer|assistant|intern|consultant|lead|specialist)\b', line, re.IGNORECASE))
    org_word = bool(re.search(r'\b(at|from)\b', line, re.IGNORECASE))
    primary_bullet = bool(re.match(r'^[^\w\s]+\s*', raw_line)) and (has_date or role_word or org_word)
    short_role_title = len(line) <= 60 and role_word and bool(re.search(r'(?:19|20)\d{2}|present|till now|till|current', next_line, re.IGNORECASE))
    return primary_bullet or short_role_title or (has_date and (role_word or org_word))


def _parse_experience_entries_v2(content: str) -> List[str]:
    raw_lines = [line for line in content.split('\n') if line.strip()]
    entries: List[str] = []
    current = ""

    for idx, raw_line in enumerate(raw_lines):
        normalized = _normalize_resume_line(raw_line)
        if not normalized:
            continue

        next_line = _normalize_resume_line(raw_lines[idx + 1]) if idx + 1 < len(raw_lines) else ""
        clean_line = re.sub(r'^[^\w\s]+', '', normalized).strip()
        lowered = clean_line.lower()

        if any(stop in lowered for stop in ["teaching /academic", "teaching academic", "projects", "education", "skills", "certifications"]):
            if current:
                entries.append(current.strip())
            break

        is_sub_bullet = bool(re.match(r'^[oâ–ªâ—¦ï‚§]\s+', raw_line.strip(), re.IGNORECASE))

        if _looks_like_experience_header_v2(clean_line, raw_line.strip(), next_line):
            if current:
                entries.append(current.strip())
            current = clean_line
        elif is_sub_bullet and current:
            current += f" {clean_line}"
        elif current:
            current += f" {clean_line}"
        else:
            current = clean_line

    if current:
        entries.append(current.strip())

    cleaned = []
    for entry in entries:
        entry = re.sub(r'\s+', ' ', entry).strip(' -')
        if entry:
            cleaned.append(entry)
    return cleaned


def _extract_education_global(text: str) -> List[str]:
    """Fallback education extraction for compact PDFs with broken section ordering."""
    lines = [_normalize_resume_line(line) for line in text.split('\n')]
    lines = [line for line in lines if line]
    results: List[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        if re.search(r'\b(university|college|school|institute)\b', line, re.IGNORECASE):
            parts = [line]
            j = i + 1
            while j < len(lines):
                nxt = lines[j]
                if re.search(r'\b(skills|experience|projects|summary|objective|languages|certifications)\b', nxt, re.IGNORECASE):
                    break
                parts.append(nxt)
                if re.search(r'\b(bachelor|master|msc|bsc|higher secondary|secondary education|engineering|science)\b', nxt, re.IGNORECASE):
                    if j + 1 < len(lines) and not re.search(r'\b(skills|experience|projects|summary|objective|languages|certifications)\b', lines[j + 1], re.IGNORECASE):
                        parts.append(lines[j + 1])
                    break
                if len(parts) >= 4:
                    break
                j += 1

            candidate = re.sub(r'\s+', ' ', " ".join(parts)).strip(" -")
            candidate = re.sub(r'(Education|Skills|Languages|Certifications)\s*$', '', candidate, flags=re.IGNORECASE).strip(" -")
            if re.search(r'\b(bachelor|master|msc|bsc|higher secondary|secondary education|engineering|science)\b', candidate, re.IGNORECASE):
                results.append(candidate)
            i = j
        i += 1

    return results


def _extract_experience_global(text: str) -> List[str]:
    """Fallback experience extraction for compact PDFs with inline company/date/title text."""
    lines = [_normalize_resume_line(line) for line in text.split('\n')]
    lines = [line for line in lines if line]
    results: List[str] = []
    i = 0

    month_pattern = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*'
    role_pattern = r'(developer|engineer|manager|analyst|officer|administrator|consultant|lead|specialist)'

    while i < len(lines):
        line = lines[i]
        headerish = re.search(month_pattern, line, re.IGNORECASE) and re.search(role_pattern, line, re.IGNORECASE)
        if headerish:
            parts = [line]
            j = i + 1
            while j < len(lines):
                nxt = lines[j]
                if re.search(r'\b(education|skills|projects|summary|objective|languages|certifications)\b', nxt, re.IGNORECASE):
                    break
                if re.search(month_pattern, nxt, re.IGNORECASE) and re.search(role_pattern, nxt, re.IGNORECASE):
                    break
                parts.append(nxt)
                if len(parts) >= 6:
                    break
                j += 1

            candidate = re.sub(r'\s+', ' ', " ".join(parts)).strip(" -")
            candidate = re.sub(r'(Education|Skills|Languages|Certifications)\s*$', '', candidate, flags=re.IGNORECASE).strip(" -")
            candidate = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', ' ', candidate)
            candidate = re.sub(r'(?<=Present)(?=[A-Za-z])', ' ', candidate)
            candidate = re.sub(r'(?<=Store)(?=Experience)', ' ', candidate)
            results.append(candidate)
            i = j
            continue
        i += 1

    return results


def enhanced_extract_sections(text: str, file_path: str = None) -> Dict[str, List[str]]:
    """Final parser override with better handling for compact PDF resumes."""
    sections = {
        "skills": [],
        "education": [],
        "experience": [],
        "certifications": []
    }

    normalized_text = _normalize_section_boundaries(text)

    if file_path and file_path.lower().endswith('.pdf'):
        try:
            sections["skills"].extend(extract_skills_from_pdf_tables(file_path))
        except Exception:
            pass

    section_patterns = {
        "skills": [
            r"^\s*(?:skills?/core\s+competencies|skills?|technical\s+skills?|technologies|expertise|competencies|core\s+competencies|proficiencies)\b[:\-\s]*(.*?)(?=^\s*(?:education|experience|work|projects|certifications|career|teaching|trainings|languages)\b|\Z)",
        ],
        "education": [
            r"^\s*(?:education|academic\s+background|qualifications|academics|degrees?)\b[:\-\s]*(.*?)(?=^\s*(?:experience|skills|work|projects|certifications|career|teaching|trainings|languages)\b|\Z)",
        ],
        "experience": [
            r"^\s*(?:experience|work\s+history|employment|professional(?:\s+experience)?|career\s+history|work\s+experience)\b[:\-\s]*(.*?)(?=^\s*(?:education|skills|projects|certifications|teaching|trainings|languages)\b|\Z)",
        ],
        "certifications": [
            r"^\s*(?:certifications?|certificates?|licenses?)\b[:\-\s]*(.*?)(?=^\s*(?:education|experience|skills|projects|languages)\b|\Z)",
        ],
    }

    skills_content = _extract_first_section(normalized_text, section_patterns["skills"])
    education_content = _extract_first_section(normalized_text, section_patterns["education"])
    experience_content = _extract_first_section(normalized_text, section_patterns["experience"])
    cert_content = _extract_first_section(normalized_text, section_patterns["certifications"])

    if skills_content:
        sections["skills"].extend(split_skills_string(skills_content))
    if education_content:
        sections["education"].extend(_parse_education_entries_v2(education_content))
    if experience_content:
        sections["experience"].extend(_parse_experience_entries_v2(experience_content))
    if cert_content:
        sections["certifications"].extend(_split_plain_section(cert_content))

    if not sections["education"]:
        sections["education"].extend(_extract_education_global(normalized_text))
    if not sections["experience"] or all(
        not re.search(r'(?:19|20)\d{2}|present|developer|engineer|manager|analyst|officer', item, re.IGNORECASE)
        for item in sections["experience"]
    ):
        sections["experience"] = _extract_experience_global(normalized_text)

    if len(sections["skills"]) < 4:
        sections["skills"].extend(extract_skills_from_text_keywords(normalized_text))

    education_like = []
    cleaned_experience = []
    edu_pattern = r'\b(bachelor|master|msc|bsc|phd|secondary education|higher secondary|university|college|school|engineering)\b'

    for entry in sections["experience"]:
        if re.search(edu_pattern, entry, re.IGNORECASE):
            education_like.append(entry)
        else:
            cleaned_experience.append(entry)

    if education_like:
        sections["education"].extend(education_like)
    sections["experience"] = cleaned_experience

    if sections["skills"]:
        sections["skills"] = clean_skill_list(sections["skills"])

    def _dedupe_keep_order(items: List[str]) -> List[str]:
        seen = set()
        result = []
        for item in items:
            normalized = re.sub(r'\s+', ' ', item).strip().lower()
            if normalized and normalized not in seen:
                seen.add(normalized)
                result.append(re.sub(r'\s+', ' ', item).strip())
        return result

    def _drop_contained(items: List[str]) -> List[str]:
        result = []
        normalized_items = [re.sub(r'\s+', ' ', item).strip() for item in items]
        for idx, item in enumerate(normalized_items):
            lower_item = item.lower()
            if any(idx != j and lower_item in other.lower() and len(other) > len(item) + 10 for j, other in enumerate(normalized_items)):
                continue
            result.append(item)
        return result

    sections["education"] = _dedupe_keep_order(sections["education"])
    sections["experience"] = _dedupe_keep_order(sections["experience"])
    sections["certifications"] = _dedupe_keep_order(sections["certifications"])
    sections["education"] = _drop_contained(sections["education"])
    sections["experience"] = _drop_contained(sections["experience"])
    sections["education"] = [
        item for item in sections["education"]
        if re.search(r'\b(university|school|college|institute)\b', item, re.IGNORECASE)
    ]

    return sections

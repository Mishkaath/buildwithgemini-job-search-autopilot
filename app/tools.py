"""Job Search Autopilot Tools.

Firestore is used as a backend to track applications and criteria.
Project ID is hardcoded for Agent Platform compatibility.
"""

import os
import uuid
import datetime
from typing import Any, Dict, List, Optional

from google import genai
from google.cloud import firestore
from google.genai import types

PROJECT_ID = "qwiklabs-gcp-02-c1c4ceadc18a"
COLLECTION_NAME = "job_applications"
CRITERIA_COLLECTION = "user_criteria"

def _get_firestore_client() -> firestore.Client:
    """Returns a Firestore client initialized with hardcoded GCP project ID."""
    return firestore.Client(project=PROJECT_ID)

def save_search_criteria(criteria_text: str) -> Dict[str, Any]:
    """Parses and saves natural language search sessions into structured filters in Firestore.
    
    Args:
        criteria_text: Natural language description of what the user is looking for.
        
    Returns:
        The structured filters saved.
    """
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    prompt = (
        "Parse the following natural language job search criteria into structured filters: "
        "Roles, Salary Bands, Locations, Skills, Company Filters.\n\n"
        f"{criteria_text}"
    )
    try:
        response = client.models.generate_content(
            model="gemini-3.1-pro",
            contents=prompt,
        )
        parsed = response.text
        
        db = _get_firestore_client()
        db.collection(CRITERIA_COLLECTION).document("active_criteria").set({
            "raw_text": criteria_text,
            "parsed": parsed,
            "last_updated": datetime.datetime.now().isoformat()
        })
        return {"status": "success", "parsed_criteria": parsed}
    except Exception as e:
        return {"error": str(e)}

def discover_jobs(query: str, location: str, criteria: str = "") -> List[Dict[str, str]]:
    """Pulls and deduplicates jobs across ATS public boards (Greenhouse, Lever, Ashby), company web searches, and news/blogs.
    
    Returns:
        List of discovered job openings (mocked for now).
    """
    return [
        {
            "id": f"job-{uuid.uuid4().hex[:6]}",
            "title": "Senior Backend Engineer",
            "company": "TechCorp Inc.",
            "location": location,
            "description": "Looking for an experienced Python developer with GCP experience...",
            "url": "https://boards.greenhouse.io/techcorp/123",
            "source": "Greenhouse",
        },
        {
            "id": f"job-{uuid.uuid4().hex[:6]}",
            "title": "Software Engineer II",
            "company": "DataFlow Systems",
            "location": location,
            "description": "Python, SQL, and robust system design skills required.",
            "url": "https://jobs.lever.co/dataflow/456",
            "source": "Lever",
        }
    ]

def score_job_fit(job_description: str) -> Dict[str, Any]:
    """Scores a job (0-100) against active criteria using skill overlap and LLM evaluation with visible rationale.
    
    Args:
        job_description: The JD for the target role.
        
    Returns:
        Dictionary with score and rationale.
    """
    db = _get_firestore_client()
    doc = db.collection(CRITERIA_COLLECTION).document("active_criteria").get()
    criteria = doc.to_dict().get("parsed", "No criteria set.") if doc.exists else "No criteria set."
    
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    prompt = (
        "Evaluate the following Job Description against the User's Criteria. "
        "Score the fit from 0 to 100 based on skill overlap, salary, location, and role match. "
        "Return the output exactly in this format:\nSCORE: [0-100]\nRATIONALE: [Your reasoning]\n\n"
        f"--- USER CRITERIA ---\n{criteria}\n\n"
        f"--- JOB DESCRIPTION ---\n{job_description}"
    )
    try:
        response = client.models.generate_content(
            model="gemini-3.1-pro",
            contents=prompt,
        )
        return {"evaluation": response.text}
    except Exception as e:
        return {"error": str(e)}

def tailor_resume(job_description: str, master_resume: str) -> str:
    """Takes a master profile and generates per-job tailored resume variants aligned to the job description without fabricating facts.
    
    Args:
        job_description: The JD for the target role.
        master_resume: The user's master resume content.
        
    Returns:
        The tailored resume text.
    """
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    prompt = (
        "You are an expert Resume Writer and Career Coach. "
        "Review the following Job Description and the candidate's Master Resume. "
        "Tailor the resume to strongly highlight matching keywords and achievements "
        "relevant to the Job Description. Do not lie or invent experience.\n\n"
        f"--- JOB DESCRIPTION ---\n{job_description}\n\n"
        f"--- MASTER RESUME ---\n{master_resume}"
    )
    
    try:
        response = client.models.generate_content(
            model="gemini-3.1-pro",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Error tailoring resume: {e}"

def track_application(
    company: str,
    title: str,
    url: str,
    status: str,
    fit_score: str = "N/A",
    tailored_resume: str = "",
    contacts: str = "",
    prep_topics: str = "",
) -> Dict[str, Any]:
    """Saves a new job application record to the Tracker Dashboard in Firestore.
    
    Args:
        company: Company name.
        title: Job title.
        url: Job posting URL.
        status: Application status (e.g., 'Discovered', 'Applied').
        fit_score: The 0-100 fit score for the job.
        tailored_resume: The customized resume used for this application.
        contacts: Known HR contacts or LinkedIn referrals.
        prep_topics: Interview preparation notes.
        
    Returns:
        Confirmation dictionary.
    """
    db = _get_firestore_client()
    doc_id = f"app-{uuid.uuid4().hex[:8]}"
    
    data = {
        "id": doc_id,
        "company": company,
        "title": title,
        "url": url,
        "status": status,
        "fit_score": fit_score,
        "date_added": datetime.datetime.now().isoformat(),
        "tailored_resume": tailored_resume,
        "contacts": contacts,
        "prep_topics": prep_topics,
        "last_updated": datetime.datetime.now().isoformat(),
    }
    
    db.collection(COLLECTION_NAME).document(doc_id).set(data)
    return {"status": "success", "message": f"Successfully tracked application at {company}.", "data": data}

def update_application_status(app_id: str, new_status: str) -> Dict[str, Any]:
    """Updates the status of an existing job application in Firestore."""
    db = _get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(app_id)
    if not doc_ref.get().exists:
        return {"error": f"Application {app_id} not found."}
        
    doc_ref.update({
        "status": new_status,
        "last_updated": datetime.datetime.now().isoformat()
    })
    return {"status": "success", "message": f"Application {app_id} status updated to '{new_status}'."}

def parse_inbound_emails() -> List[Dict[str, str]]:
    """Parses inbound notifications/emails to auto-advance application statuses.
    
    Returns:
        A list of new status updates discovered in the inbox.
    """
    # Mock implementation of Email Intelligence
    return [
        {
            "company": "TechCorp Inc.",
            "subject": "Interview Invitation: Senior Backend Engineer",
            "detected_status": "Interviewing",
            "action": "Auto-advanced status to Interviewing",
        }
    ]

def research_interview_and_referrals(company_name: str) -> str:
    """Performs a web search to find common interview questions and referral paths for a company."""
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    prompt = (
        f"Perform a simulated web research on the company '{company_name}'. "
        "Summarize the most commonly asked technical and behavioral interview questions "
        "for software engineering roles at this company. Also, suggest networking strategies "
        "or departments to look up on LinkedIn for employee referrals."
    )
    
    try:
        response = client.models.generate_content(
            model="gemini-3.1-pro",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Research error: {e}"

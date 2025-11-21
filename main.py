import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List
from database import db, create_document
from schemas import Lead
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI(title="NV Media API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "NV Media Backend Running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:60]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:60]}"
    return response

# Email utility
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "support@nvmedia.in")
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
FROM_EMAIL = os.getenv("FROM_EMAIL", SUPPORT_EMAIL)


def send_email(subject: str, html_body: str, to_emails: List[str]):
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
        # In this environment, SMTP may not be configured. We won't fail the request.
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = FROM_EMAIL
        msg["To"] = ", ".join(to_emails)
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(FROM_EMAIL, to_emails, msg.as_string())
        return True
    except Exception:
        return False


class LeadCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str | None = None
    company: str | None = None
    service: str
    budget: str
    message: str | None = None


@app.post("/api/leads")
def create_lead(payload: LeadCreate):
    try:
        # Validate via schema
        lead = Lead(**payload.model_dump())

        # Store in DB
        inserted_id = create_document("lead", lead)

        # Send email to support
        html = f"""
        <h2>New Inquiry - NV Media</h2>
        <p><strong>Name:</strong> {lead.full_name}</p>
        <p><strong>Email:</strong> {lead.email}</p>
        <p><strong>Phone:</strong> {lead.phone or '-'} </p>
        <p><strong>Company:</strong> {lead.company or '-'} </p>
        <p><strong>Service:</strong> {lead.service}</p>
        <p><strong>Budget:</strong> {lead.budget}</p>
        <p><strong>Message:</strong><br/>{(lead.message or '').replace('\n','<br/>')}</p>
        """
        send_email("New NV Media Inquiry", html, [SUPPORT_EMAIL])

        # Optional auto-reply to user (best-effort)
        auto_html = f"""
        <p>Hi {lead.full_name.split(' ')[0]},</p>
        <p>Thanks for reaching out to NV Media. Our team will review your inquiry and get back to you shortly.</p>
        <p>Best,<br/>NV Media</p>
        """
        send_email("Thanks for contacting NV Media", auto_html, [lead.email])

        return {"status": "success", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

import uuid
import random
from pydantic import BaseModel, Field
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import win32com.client as win32
import plotly.graph_objects as go

# Define the DisasterAlert class using Pydantic
class DisasterAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    headline: str
    summary: str
    criticality: str
    location: str
    time_of_impact: str
    disaster_severity: float
    days_of_impact: int

# Simulated database of regional data
region_data = {
    "Bangalore, India": {
        "server_count": 200,
        "critical_services": 25,
        "employee_count": 750,
        "support_redundancy": 0.85,
        "resilience": 0.9,
        "data_center_capacity": 95,
        "backup_facilities": 2,
        "technical_teams": 10,
        "business_critical_teams": 5,
    },
    "Santiago, Chile": {
        "server_count": 100,
        "critical_services": 10,
        "employee_count": 300,
        "support_redundancy": 0.75,
        "resilience": 0.7,
        "data_center_capacity": 80,
        "backup_facilities": 1,
        "technical_teams": 5,
        "business_critical_teams": 2,
    }
}

# Function to fetch regional data
def fetch_region_data(location):
    return region_data.get(location, {})

# Load a pre-trained BERT model for sequence classification
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased')

# Function to classify text using BERT
def classify_text(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.logits.argmax().item()

# Function to calculate impact based on predefined criteria
def calculate_impact(data):
    weights = {
        'server_count': 0.15,
        'critical_services': 0.15,
        'employee_count': 0.1,
        'support_redundancy': 0.1,
        'resilience': 0.1,
        'days_of_impact': 0.05,
        'geographical_spread': 0.1,
        'disaster_severity': 0.1,
        'time_of_impact': 0.05,
        'preventive_measures': 0.1,
        'data_center_capacity': 0.05,
        'backup_facilities': 0.05,
        'technical_teams': 0.025,
        'business_critical_teams': 0.025,
    }
    impact_score = sum(data.get(key, 0) * weights[key] for key in weights)
    return impact_score * 100

# Function to create risk graphs with Plotly
def create_risk_graph(data):
    labels = list(data.keys())
    values = list(data.values())
    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig.update_layout(title='Risk Assessment Breakdown')
    fig.write_image("risk_assessment.png")
    return "risk_assessment.png"

# Function to find resolution based on keywords
resolution_guidelines = {
    "flood": "Ensure all electrical devices are elevated. Follow evacuation plan X. Contact flood response team Y.",
    "earthquake": "Inspect structural integrity. Follow evacuation plan Z. Assess and report damages to team Y."
}

def find_resolution(text):
    for key, resolution in resolution_guidelines.items():
        if key in text.lower():
            return resolution
    return "No specific resolution available. Follow general safety measures."

# Function to send notification via Outlook
def send_notification(subject, body, to_recipients, attachment_path):
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.Subject = subject
    mail.Body = body
    mail.To = to_recipients
    mail.Attachments.Add(attachment_path)
    mail.Send()

# Main function to orchestrate the flow
def main():
    alerts = [
        {
            "headline": "Major Flood in Bangalore",
            "summary": "Severe flooding reported in Bangalore, India after heavy rainfall.",
            "criticality": "High",
            "location": "Bangalore, India",
            "time_of_impact": "Peak Hours",
            "disaster_severity": 0.9,
            "days_of_impact": 3
        },
        {
            "headline": "Earthquake in Chile",
            "summary": "A 6.5 magnitude earthquake has struck northern Chile.",
            "criticality": "Medium",
            "location": "Santiago, Chile",
            "time_of_impact": "Non-Peak",
            "disaster_severity": 0.7,
            "days_of_impact": 1
        }
    ]

    for alert_data in alerts:
        alert = DisasterAlert(**alert_data)
        regional_data = fetch_region_data(alert.location)
        if regional_data:
            impact_data = {**regional_data, **{
                'days_of_impact': alert.days_of_impact,
                'disaster_severity': alert.disaster_severity,
                'time_of_impact': 0.8 if alert.time_of_impact == 'Peak Hours' else 0.2,
                'preventive_measures': 0.7
            }}
            impact_percentage = calculate_impact(impact_data)
            graph_path = create_risk_graph(impact_data)
            resolution_text = find_resolution(alert.summary)
            if impact_percentage > 50:
                subject = f"Urgent: Impact Notification for {alert.location}"
                body = f"Critical alert: {alert.headline}\nImpact: {impact_percentage}%\nEmployees affected: {regional_data['employee_count']}\nResolution Steps: {resolution_text}\nPlease follow the disaster recovery protocol immediately."
                send_notification(subject, body, 'safety_team@example.com', graph_path)

if __name__ == "__main__":
    main()


# Expanded simulated database of regional data
region_data = {
    "Bangalore, India": {
        "server_count": 200,
        "critical_services": 25,
        "employee_count": 750,
        "support_redundancy": 0.85,
        "resilience": 0.9,
        "data_center_capacity": 95,
        "backup_facilities": 2,
        "technical_teams": 10,
        "business_critical_teams": 5,
    },
    "Santiago, Chile": {
        "server_count": 100,
        "critical_services": 10,
        "employee_count": 300,
        "support_redundancy": 0.75,
        "resilience": 0.7,
        "data_center_capacity": 80,
        "backup_facilities": 1,
        "technical_teams": 5,
        "business_critical_teams": 2,
    },
    "New York, USA": {
        "server_count": 300,
        "critical_services": 30,
        "employee_count": 1000,
        "support_redundancy": 0.9,
        "resilience": 0.95,
        "data_center_capacity": 90,
        "backup_facilities": 3,
        "technical_teams": 12,
        "business_critical_teams": 7,
    },
    "Tokyo, Japan": {
        "server_count": 250,
        "critical_services": 20,
        "employee_count": 800,
        "support_redundancy": 0.88,
        "resilience": 0.92,
        "data_center_capacity": 93,
        "backup_facilities": 2,
        "technical_teams": 11,
        "business_critical_teams": 6,
    },
    "London, UK": {
        "server_count": 150,
        "critical_services": 15,
        "employee_count": 500,
        "support_redundancy": 0.82,
        "resilience": 0.85,
        "data_center_capacity": 87,
        "backup_facilities": 2,
        "technical_teams": 8,
        "business_critical_teams": 4,
    },
    "Sydney, Australia": {
        "server_count": 120,
        "critical_services": 12,
        "employee_count": 400,
        "support_redundancy": 0.80,
        "resilience": 0.83,
        "data_center_capacity": 85,
        "backup_facilities": 1,
        "technical_teams": 7,
        "business_critical_teams": 3,
    }
}

# Function to fetch regional data based on location
def fetch_region_data(location):
    return region_data.get(location, {})

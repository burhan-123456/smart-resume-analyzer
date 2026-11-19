
# Smart Resume Analyzer

A web-based Smart Resume Analyzer developed using
Python, Flask, Streamlit, and SQLite.

The application helps organize candidate profiles,
compare skills against job requirements, calculate
matching scores, and visualize recruitment statistics.

## Features

### Candidate Management
- Register new candidates
- Store candidate information in SQLite
- View saved candidates
- Search candidates by name
- Filter candidates by skills
- Update candidate information
- Delete candidate records

### Resume Analysis
- Extract keywords from job descriptions
- Compare candidate and required skills
- Calculate skill matching percentage
- Identify matched skills
- Identify missing skills
- Generate skill improvement suggestions

### Resume Scoring
- Calculate experience score
- Calculate education score
- Calculate weighted overall score
- Display scores using progress indicators

### Candidate Ranking
- Rank candidates by skill match
- Compare two candidates
- Display top five matching candidates

### Analytics
- Dashboard statistics
- Skill frequency analysis
- Skill frequency bar chart
- Save analysis history
- View previous analyses

### Additional Features
- Export candidate data to CSV
- Input validation
- API error handling
- API health check
- Modern Streamlit dashboard

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| Flask | REST API backend |
| Streamlit | Frontend dashboard |
| SQLite | Database |
| Pandas | Data processing |
| Requests | HTTP communication |
| Git | Version control |
| GitHub | Source code hosting |

## Project Structure

    smart-resume-analyzer/
    |
    |-- api.py
    |-- app.py
    |-- database.py
    |-- services.py
    |-- requirements.txt
    |-- README.md

## Installation

### 1. Clone the repository

    git clone YOUR_REPOSITORY_URL

    cd smart-resume-analyzer

### 2. Create a virtual environment

Windows:

    python -m venv venv
    venv\Scripts\activate

Linux/macOS:

    python3 -m venv venv
    source venv/bin/activate

### 3. Install dependencies

    pip install -r requirements.txt

The project uses Flask, Streamlit, Requests, and Pandas.

### 4. Start Flask Backend

    python api.py

Backend URL:

    http://127.0.0.1:5000

### 5. Start Streamlit Frontend

Open another terminal:

    streamlit run app.py

Streamlit will display the local application URL.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | / | API information |
| GET | /health | API health status |
| GET | /database-status | Database connection |
| POST | /submit-resume | Save resume |
| GET | /resumes | Get candidates |
| PUT | /resumes/{id} | Update candidate |
| DELETE | /resumes/{id} | Delete candidate |
| POST | /extract-keywords | Extract keywords |
| POST | /compare-skills | Compare skills |
| POST | /experience-score | Experience score |
| POST | /education-score | Education score |
| POST | /overall-score | Overall score |
| POST | /rank-candidates | Rank candidates |
| GET | /search-candidates | Search candidates |
| GET | /filter-skills | Filter by skill |
| POST | /save-analysis | Save analysis |
| GET | /analysis-history | Analysis history |
| GET | /skill-frequency | Skill frequency |
| GET | /statistics | Dashboard statistics |
| POST | /compare-candidates | Compare candidates |
| POST | /top-candidates | Top five candidates |
| GET | /export-candidates | Export CSV |

## Scoring Method

The application uses a rule-based weighted score.

Overall Score:

    60% Skill Score
    + 25% Experience Score
    + 15% Education Score

Example:

    Skill Score = 80
    Experience Score = 60
    Education Score = 75

    Overall Score =
        (80 * 0.60)
        + (60 * 0.25)
        + (75 * 0.15)

    Overall Score = 74.25%

These scores are educational heuristics and should
not be treated as validated hiring assessments.

## Example Skill Comparison

Candidate Skills:

    Python, SQL, Flask

Required Skills:

    Python, SQL, Machine Learning, Flask

Results:

    Matched Skills:
    Python, SQL, Flask

    Missing Skills:
    Machine Learning

    Match Percentage:
    75%

## Future Enhancements

- PDF resume uploading
- DOCX resume parsing
- Automatic resume text extraction
- NLP-based skill extraction
- Semantic similarity using embeddings
- Candidate authentication
- Role-based authorization
- Automated testing
- Cloud deployment

## Security Note

This project is intended for local development
and educational demonstrations.

Before deploying publicly, add authentication,
authorization, appropriate data protection,
and production database configuration.

Do not expose real candidate personal data
through an unauthenticated public API.

## Author

Developed as a Python full-stack portfolio project.

## License

For educational and portfolio purposes.

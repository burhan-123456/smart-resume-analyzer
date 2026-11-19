
import unittest
from unittest.mock import patch

from api import app


class TestResumeAPI(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_home_endpoint(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["status"],
            "running"
        )

    def test_invalid_resume(self):
        response = self.client.post(
            "/submit-resume",
            json={"name": "Test"}
        )

        self.assertEqual(response.status_code, 400)

    def test_valid_resume(self):
        payload = {
            "name": "Test Candidate",
            "email": "test@example.com",
            "skills": "Python, SQL",
            "experience": 2,
            "education": "BTech"
        }

        with patch("api.save_resume", return_value=101):
            response = self.client.post(
                "/submit-resume",
                json=payload
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.get_json()["resume_id"],
            101
        )

    def test_keyword_extraction(self):
        response = self.client.post(
            "/extract-keywords",
            json={
                "description":
                "Python and SQL skills required"
            }
        )

        self.assertEqual(response.status_code, 200)

        result = response.get_json()
        self.assertIn("python", result["keywords"])
        self.assertIn("sql", result["keywords"])

    def test_skill_comparison(self):
        response = self.client.post(
            "/compare-skills",
            json={
                "candidate_skills": "Python, SQL",
                "required_skills": "Python, Java"
            }
        )

        self.assertEqual(response.status_code, 200)

        result = response.get_json()

        self.assertEqual(result["score"], 50.0)
        self.assertIn("java", result["missing"])

    def test_experience_score(self):
        response = self.client.post(
            "/experience-score",
            json={"experience": 5}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["experience_score"],
            100
        )

    def test_education_score(self):
        response = self.client.post(
            "/education-score",
            json={"education": "BTech"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["education_score"],
            75
        )

    def test_overall_score(self):
        response = self.client.post(
            "/overall-score",
            json={
                "skill_score": 100,
                "experience": 5,
                "education": "PhD"
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["overall_score"],
            100.0
        )

    @patch("api.get_all_resumes", return_value=[])
    def test_empty_resumes(self, mock_resumes):
        response = self.client.get("/resumes")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    @patch("api.get_all_resumes", return_value=[])
    def test_empty_top_candidates(self, mock_resumes):
        response = self.client.post(
            "/top-candidates",
            json={"required_skills": "Python"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_invalid_comparison(self):
        response = self.client.post(
            "/compare-candidates",
            json={
                "candidate_id_1": 1,
                "candidate_id_2": 1,
                "required_skills": "Python"
            }
        )

        self.assertEqual(response.status_code, 400)

    @patch("api.get_candidate", return_value=None)
    def test_missing_candidate_insights(self, mock_candidate):
        response = self.client.get(
            "/candidate-insights/999"
        )

        self.assertEqual(response.status_code, 404)

    @patch("api.get_candidate")
    def test_candidate_insights(self, mock_candidate):
        mock_candidate.return_value = {
            "id": 1,
            "name": "Test Candidate",
            "email": "test@example.com",
            "skills": "python, sql",
            "experience": 2,
            "education": "btech"
        }

        response = self.client.get(
            "/candidate-insights/1"
        )

        self.assertEqual(response.status_code, 200)

        result = response.get_json()

        self.assertEqual(result["total_skills"], 2)
        self.assertEqual(result["education_score"], 75)
        self.assertEqual(result["experience_score"], 60)

    @patch("api.get_all_resumes", return_value=[])
    def test_csv_export(self, mock_resumes):
        response = self.client.get(
            "/export-candidates"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "text/csv",
            response.content_type
        )
        self.assertIn(
            "ID,Name,Email",
            response.get_data(as_text=True)
        )


if __name__ == "__main__":
    unittest.main()

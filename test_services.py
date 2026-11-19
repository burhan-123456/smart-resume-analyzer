
import unittest

from services import (
    parse_skills,
    extract_keywords,
    compare_skills,
    calculate_match_score,
    calculate_experience_score,
    calculate_education_score,
    calculate_overall_score,
    normalize_education,
    validate_resume
)


class TestResumeServices(unittest.TestCase):

    def test_parse_skills(self):
        result = parse_skills("Python, SQL, python")
        self.assertEqual(result, ["python", "sql"])

    def test_empty_skills(self):
        self.assertEqual(parse_skills(""), [])

    def test_keyword_extraction(self):
        keywords = extract_keywords(
            "Python and SQL skills required"
        )
        self.assertIn("python", keywords)
        self.assertIn("sql", keywords)

    def test_compare_skills(self):
        result = compare_skills(
            "Python, SQL",
            "Python, Java"
        )
        self.assertEqual(result["matched"], ["python"])
        self.assertEqual(result["missing"], ["java"])

    def test_full_skill_match(self):
        score = calculate_match_score(
            "Python, SQL",
            "Python, SQL"
        )
        self.assertEqual(score, 100.0)

    def test_partial_skill_match(self):
        score = calculate_match_score(
            "Python",
            "Python, SQL"
        )
        self.assertEqual(score, 50.0)

    def test_no_skill_match(self):
        score = calculate_match_score(
            "Java",
            "Python, SQL"
        )
        self.assertEqual(score, 0.0)

    def test_no_required_skills(self):
        score = calculate_match_score(
            "Python",
            ""
        )
        self.assertEqual(score, 0.0)

    def test_experience_score(self):
        self.assertEqual(
            calculate_experience_score(5), 100
        )
        self.assertEqual(
            calculate_experience_score(3), 80
        )
        self.assertEqual(
            calculate_experience_score(1), 60
        )
        self.assertEqual(
            calculate_experience_score(0), 20
        )

    def test_education_normalization(self):
        self.assertEqual(
            normalize_education("  BTech  CSE  "),
            "btech cse"
        )

    def test_education_score(self):
        self.assertEqual(
            calculate_education_score("PhD"), 100
        )
        self.assertEqual(
            calculate_education_score("MTech"), 90
        )
        self.assertEqual(
            calculate_education_score("BTech"), 75
        )
        self.assertEqual(
            calculate_education_score("Diploma"), 60
        )

    def test_overall_score(self):
        score = calculate_overall_score(
            100, 5, "PhD"
        )
        self.assertEqual(score, 100.0)

    def test_weighted_overall_score(self):
        score = calculate_overall_score(
            80, 1, "BTech"
        )
        self.assertEqual(score, 74.25)

    def test_valid_resume(self):
        data = {
            "name": "Test Candidate",
            "email": "test@example.com",
            "skills": "Python, SQL",
            "experience": 2,
            "education": "BTech"
        }

        cleaned, error = validate_resume(data)

        self.assertIsNone(error)
        self.assertEqual(
            cleaned["skills"],
            "python, sql"
        )
        self.assertEqual(
            cleaned["education"],
            "btech"
        )

    def test_invalid_email(self):
        data = {
            "name": "Test Candidate",
            "email": "invalid-email",
            "skills": "Python",
            "experience": 1,
            "education": "BTech"
        }

        cleaned, error = validate_resume(data)

        self.assertIsNone(cleaned)
        self.assertEqual(
            error,
            "Invalid email address"
        )

    def test_invalid_experience(self):
        data = {
            "name": "Test Candidate",
            "email": "test@example.com",
            "skills": "Python",
            "experience": -2,
            "education": "BTech"
        }

        cleaned, error = validate_resume(data)

        self.assertIsNone(cleaned)
        self.assertEqual(
            error,
            "Experience must be between 0 and 50"
        )

    def test_missing_fields(self):
        cleaned, error = validate_resume({
            "name": "Test Candidate"
        })

        self.assertIsNone(cleaned)
        self.assertIn(
            "Missing required fields",
            error
        )

    def test_unexpected_fields(self):
        data = {
            "name": "Test Candidate",
            "email": "test@example.com",
            "skills": "Python",
            "experience": 1,
            "education": "BTech",
            "unknown": "value"
        }

        cleaned, error = validate_resume(data)

        self.assertIsNone(cleaned)
        self.assertIn(
            "Unexpected fields",
            error
        )


if __name__ == "__main__":
    unittest.main()

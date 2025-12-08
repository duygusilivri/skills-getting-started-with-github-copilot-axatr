"""
Test suite for Mergington High School API

Tests all the endpoints including:
- Root redirect
- Getting activities
- Signing up for activities
- Unregistering from activities
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Practice basketball skills and compete in inter-school tournaments",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "lucas@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Learn swimming techniques and train for competitions",
            "schedule": "Wednesdays, 3:00 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["emily@mergington.edu", "ava@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore various art mediums including painting, drawing, and sculpture",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["isabella@mergington.edu", "mia@mergington.edu"]
        },
        "Drama Club": {
            "description": "Participate in theater productions and develop acting skills",
            "schedule": "Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["william@mergington.edu", "charlotte@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking through competitive debates",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["alexander@mergington.edu", "amelia@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Compete in science and engineering challenges at regional competitions",
            "schedule": "Fridays, 3:00 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["benjamin@mergington.edu", "harper@mergington.edu"]
        }
    }
    
    # Reset to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Clean up after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root path redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for getting activities"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        
    def test_activities_have_correct_structure(self, client):
        """Test that each activity has the required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for signing up for activities"""
    
    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify the participant was added
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client):
        """Test signing up for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate_participant(self, client):
        """Test that a student cannot sign up twice for the same activity"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_adds_to_participants_list(self, client):
        """Test that signup actually adds participant to the list"""
        email = "test@mergington.edu"
        activity_name = "Programming Class"
        
        # Get initial count
        initial_count = len(activities[activity_name]["participants"])
        
        # Sign up
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Verify count increased
        assert len(activities[activity_name]["participants"]) == initial_count + 1
        assert email in activities[activity_name]["participants"]


class TestUnregisterFromActivity:
    """Tests for unregistering from activities"""
    
    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        email = "michael@mergington.edu"  # Currently in Chess Club
        response = client.delete(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email in data["message"]
        
        # Verify the participant was removed
        assert email not in activities["Chess Club"]["participants"]
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregistering from an activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_not_signed_up(self, client):
        """Test unregistering a student who is not signed up"""
        email = "notsignedup@mergington.edu"
        response = client.delete(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_removes_from_participants_list(self, client):
        """Test that unregister actually removes participant from the list"""
        email = "emma@mergington.edu"  # Currently in Programming Class
        activity_name = "Programming Class"
        
        # Get initial count
        initial_count = len(activities[activity_name]["participants"])
        
        # Unregister
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        assert response.status_code == 200
        
        # Verify count decreased
        assert len(activities[activity_name]["participants"]) == initial_count - 1
        assert email not in activities[activity_name]["participants"]


class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_signup_and_unregister_workflow(self, client):
        """Test complete workflow of signing up and then unregistering"""
        email = "workflow@mergington.edu"
        activity_name = "Drama Club"
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        assert email not in activities[activity_name]["participants"]
    
    def test_multiple_signups_different_activities(self, client):
        """Test signing up the same student for multiple activities"""
        email = "multisport@mergington.edu"
        
        # Sign up for multiple activities
        activities_to_join = ["Chess Club", "Art Club", "Science Olympiad"]
        
        for activity_name in activities_to_join:
            response = client.post(
                f"/activities/{activity_name}/signup?email={email}"
            )
            assert response.status_code == 200
            assert email in activities[activity_name]["participants"]

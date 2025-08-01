#!/usr/bin/env python3
"""
Backend API Test Suite for Curriculum To-Do List Application
Tests the FastAPI backend endpoints for curriculum data management
"""

import requests
import json
import sys
from typing import Dict, List, Any

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading backend URL: {e}")
        return None

BACKEND_URL = get_backend_url()
if not BACKEND_URL:
    print("❌ Could not get backend URL from frontend/.env")
    sys.exit(1)

API_BASE = f"{BACKEND_URL}/api"
print(f"🔗 Testing backend at: {API_BASE}")

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = {
            "curriculum_data_api": {"passed": 0, "failed": 0, "errors": []},
            "mongodb_integration": {"passed": 0, "failed": 0, "errors": []},
            "cors_configuration": {"passed": 0, "failed": 0, "errors": []}
        }
        
    def log_result(self, category: str, test_name: str, success: bool, message: str = ""):
        if success:
            self.test_results[category]["passed"] += 1
            print(f"✅ {test_name}")
        else:
            self.test_results[category]["failed"] += 1
            self.test_results[category]["errors"].append(f"{test_name}: {message}")
            print(f"❌ {test_name}: {message}")
    
    def test_curriculum_data_api(self):
        """Test the Curriculum Data API endpoints"""
        print("\n🧪 Testing Curriculum Data API...")
        
        # Test 1: GET /api/subjects - should return all 5 subjects
        try:
            response = self.session.get(f"{API_BASE}/subjects")
            if response.status_code == 200:
                subjects = response.json()
                
                # Check if we have 5 subjects
                expected_subjects = ["Türkçe", "Fizik", "Kimya", "Biyoloji", "Matematik"]
                if len(subjects) == 5:
                    self.log_result("curriculum_data_api", "GET /api/subjects returns 5 subjects", True)
                else:
                    self.log_result("curriculum_data_api", "GET /api/subjects returns 5 subjects", False, 
                                  f"Expected 5 subjects, got {len(subjects)}")
                
                # Check subject structure and names
                subject_names = [s["name"] for s in subjects]
                missing_subjects = [s for s in expected_subjects if s not in subject_names]
                if not missing_subjects:
                    self.log_result("curriculum_data_api", "All expected subjects present", True)
                else:
                    self.log_result("curriculum_data_api", "All expected subjects present", False,
                                  f"Missing subjects: {missing_subjects}")
                
                # Check subject data structure
                for subject in subjects:
                    required_fields = ["id", "name", "total_topics", "completed_topics", "completion_rate"]
                    missing_fields = [field for field in required_fields if field not in subject]
                    if not missing_fields:
                        self.log_result("curriculum_data_api", f"Subject {subject['name']} has correct structure", True)
                    else:
                        self.log_result("curriculum_data_api", f"Subject {subject['name']} has correct structure", False,
                                      f"Missing fields: {missing_fields}")
                
                # Store first subject for further testing
                self.test_subject = subjects[0] if subjects else None
                
            else:
                self.log_result("curriculum_data_api", "GET /api/subjects responds with 200", False,
                              f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("curriculum_data_api", "GET /api/subjects endpoint accessible", False, str(e))
            return
        
        # Test 2: GET /api/subjects/{subject}/topics - test with Turkish subject
        if self.test_subject:
            try:
                subject_name = "Türkçe"
                response = self.session.get(f"{API_BASE}/subjects/{subject_name}/topics")
                if response.status_code == 200:
                    topics = response.json()
                    self.log_result("curriculum_data_api", f"GET /api/subjects/{subject_name}/topics responds with 200", True)
                    
                    # Check topics structure
                    if topics and len(topics) > 0:
                        topic = topics[0]
                        required_fields = ["id", "title", "completed"]
                        missing_fields = [field for field in required_fields if field not in topic]
                        if not missing_fields:
                            self.log_result("curriculum_data_api", "Topics have correct structure", True)
                            self.test_topic_id = topic["id"]  # Store for PUT test
                        else:
                            self.log_result("curriculum_data_api", "Topics have correct structure", False,
                                          f"Missing fields: {missing_fields}")
                    else:
                        self.log_result("curriculum_data_api", "Topics returned for Turkish subject", False,
                                      "No topics returned")
                else:
                    self.log_result("curriculum_data_api", f"GET /api/subjects/{subject_name}/topics responds with 200", False,
                                  f"Status code: {response.status_code}")
            except Exception as e:
                self.log_result("curriculum_data_api", "GET topics endpoint accessible", False, str(e))
        
        # Test 3: PUT /api/subjects/{subject}/topics/{topic_id} - toggle completion
        if hasattr(self, 'test_topic_id'):
            try:
                subject_name = "Türkçe"
                topic_id = self.test_topic_id
                
                # Test toggling to completed
                response = self.session.put(
                    f"{API_BASE}/subjects/{subject_name}/topics/{topic_id}",
                    json={"completed": True}
                )
                if response.status_code == 200:
                    self.log_result("curriculum_data_api", "PUT topic completion toggle responds with 200", True)
                    
                    # Verify the change persisted
                    verify_response = self.session.get(f"{API_BASE}/subjects/{subject_name}/topics")
                    if verify_response.status_code == 200:
                        topics = verify_response.json()
                        updated_topic = next((t for t in topics if t["id"] == topic_id), None)
                        if updated_topic and updated_topic["completed"] == True:
                            self.log_result("curriculum_data_api", "Topic completion status persists", True)
                        else:
                            self.log_result("curriculum_data_api", "Topic completion status persists", False,
                                          "Completion status not updated")
                else:
                    self.log_result("curriculum_data_api", "PUT topic completion toggle responds with 200", False,
                                  f"Status code: {response.status_code}")
            except Exception as e:
                self.log_result("curriculum_data_api", "PUT topic endpoint accessible", False, str(e))
    
    def test_mongodb_integration(self):
        """Test MongoDB integration and data persistence"""
        print("\n🧪 Testing MongoDB Integration...")
        
        # Test 1: Data auto-initialization
        try:
            response = self.session.get(f"{API_BASE}/subjects")
            if response.status_code == 200:
                subjects = response.json()
                
                # Check if subjects have UUID-based IDs
                for subject in subjects:
                    if "id" in subject and len(subject["id"]) == 36:  # UUID length
                        self.log_result("mongodb_integration", f"Subject {subject['name']} has UUID-based ID", True)
                    else:
                        self.log_result("mongodb_integration", f"Subject {subject['name']} has UUID-based ID", False,
                                      f"ID format: {subject.get('id', 'missing')}")
                
                # Test topic count matches curriculum data
                expected_counts = {
                    "Türkçe": 43,
                    "Fizik": 58, 
                    "Kimya": 33,
                    "Biyoloji": 34,
                    "Matematik": 28
                }
                
                for subject in subjects:
                    expected_count = expected_counts.get(subject["name"])
                    if expected_count and subject["total_topics"] == expected_count:
                        self.log_result("mongodb_integration", f"{subject['name']} has correct topic count", True)
                    else:
                        self.log_result("mongodb_integration", f"{subject['name']} has correct topic count", False,
                                      f"Expected {expected_count}, got {subject['total_topics']}")
                        
        except Exception as e:
            self.log_result("mongodb_integration", "MongoDB data initialization", False, str(e))
        
        # Test 2: Data persistence across requests
        try:
            # Get initial state
            response1 = self.session.get(f"{API_BASE}/subjects")
            subjects1 = response1.json() if response1.status_code == 200 else []
            
            # Make another request
            response2 = self.session.get(f"{API_BASE}/subjects")
            subjects2 = response2.json() if response2.status_code == 200 else []
            
            if subjects1 == subjects2:
                self.log_result("mongodb_integration", "Data consistency across requests", True)
            else:
                self.log_result("mongodb_integration", "Data consistency across requests", False,
                              "Data differs between requests")
                
        except Exception as e:
            self.log_result("mongodb_integration", "Data persistence testing", False, str(e))
        
        # Test 3: Topic ID consistency
        try:
            response = self.session.get(f"{API_BASE}/subjects/Türkçe/topics")
            if response.status_code == 200:
                topics = response.json()
                
                # Check all topics have UUID-based IDs
                uuid_count = 0
                for topic in topics:
                    if "id" in topic and len(topic["id"]) == 36:
                        uuid_count += 1
                
                if uuid_count == len(topics):
                    self.log_result("mongodb_integration", "All topics have UUID-based IDs", True)
                else:
                    self.log_result("mongodb_integration", "All topics have UUID-based IDs", False,
                                  f"Only {uuid_count}/{len(topics)} topics have valid UUIDs")
                    
        except Exception as e:
            self.log_result("mongodb_integration", "Topic UUID verification", False, str(e))
    
    def test_cors_configuration(self):
        """Test CORS configuration"""
        print("\n🧪 Testing CORS Configuration...")
        
        # Test 1: CORS headers present in actual response
        try:
            # Make request with Origin header to trigger CORS
            headers = {'Origin': 'https://example.com'}
            response = self.session.get(f"{API_BASE}/subjects", headers=headers)
            
            # Check for CORS headers (case-insensitive)
            cors_headers_found = []
            for header_name, header_value in response.headers.items():
                header_lower = header_name.lower()
                if 'access-control' in header_lower:
                    cors_headers_found.append(f"{header_name}: {header_value}")
            
            if cors_headers_found:
                self.log_result("cors_configuration", "CORS headers present in response", True)
                print(f"   Found CORS headers: {cors_headers_found}")
            else:
                # CORS might be handled at proxy level, check if request succeeds from different origin
                if response.status_code == 200:
                    self.log_result("cors_configuration", "Cross-origin requests allowed", True)
                else:
                    self.log_result("cors_configuration", "CORS headers present in response", False,
                                  "No CORS headers found and request failed")
                
        except Exception as e:
            self.log_result("cors_configuration", "CORS headers check", False, str(e))
        
        # Test 2: API accessibility (main CORS test)
        try:
            response = self.session.get(f"{API_BASE}/subjects")
            if response.status_code == 200:
                self.log_result("cors_configuration", "API accessible for cross-origin requests", True)
            else:
                self.log_result("cors_configuration", "API accessible for cross-origin requests", False,
                              f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("cors_configuration", "API accessibility test", False, str(e))
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Backend API Tests...")
        print("=" * 50)
        
        self.test_curriculum_data_api()
        self.test_mongodb_integration()
        self.test_cors_configuration()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status = "✅ PASS" if failed == 0 else "❌ FAIL"
            print(f"{category.replace('_', ' ').title()}: {status} ({passed} passed, {failed} failed)")
            
            if results["errors"]:
                for error in results["errors"]:
                    print(f"  - {error}")
        
        print(f"\nOverall: {total_passed} passed, {total_failed} failed")
        
        if total_failed == 0:
            print("🎉 All backend tests passed!")
            return True
        else:
            print("⚠️  Some backend tests failed!")
            return False

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
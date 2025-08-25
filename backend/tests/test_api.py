import pytest
from datetime import date
from fastapi.testclient import TestClient

class TestBasicAPI:
    """Basic API endpoint tests"""
    
    def test_health_check(self, client: TestClient):
        """Test if the API is running"""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_get_todos_empty(self, client: TestClient):
        """Test getting todos when none exist"""
        response = client.get("/api/todoapp")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_todos_with_data(self, client: TestClient, sample_todo):
        """Test getting todos when they exist"""
        response = client.get("/api/todoapp")
        assert response.status_code == 200
        todos = response.json()
        assert len(todos) == 1
        assert todos[0]["title"] == "Sample Item"
    
    def test_get_todo_by_id(self, client: TestClient, sample_todo):
        """Test getting a specific todo by ID"""
        todo_id = sample_todo.id
        response = client.get(f"/api/todoapp/{todo_id}")
        assert response.status_code == 200
        todo = response.json()
        assert todo["id"] == todo_id
        assert todo["title"] == "Sample Item"
        
    def test_create_todo_success(self, client: TestClient):
        """Test creating a new todo"""
        todo_data = {
            "title": "Hello",
            "description": "World"
        }
        today = date.today().isoformat()
        
        response = client.post(
            f"/api/todoapp?selected_date={today}",
            json=todo_data
        )
        
        # Debug output
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.json()}")
            print(f"Request data: {todo_data}")
            print(f"Request URL: /api/todoapp?selected_date={today}")
        
        assert response.status_code == 200
        todo = response.json()
        assert todo["title"] == todo_data["title"]
        assert todo["description"] == todo_data["description"]
        assert todo["date"] == today
        assert not todo["completed"]
        
    def test_update_todo_success(self, client: TestClient, sample_todo):
        """Test updating a todo"""
        todo_id = sample_todo.id
        update_data = {
            "title": "Hello",
            "completed": True
        }
        
        response = client.put(
            f"/api/todoapp/{todo_id}",
            json=update_data
        )
        
        # Debug output
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.json()}")
            print(f"Request data: {update_data}")
        
        assert response.status_code == 200
        todo = response.json()
        assert todo["title"] == update_data["title"]
        assert todo["completed"] == update_data["completed"]
    
    def test_delete_todo_success(self, client: TestClient, sample_todo):
        """Test deleting a todo"""
        todo_id = sample_todo.id
        response = client.delete(f"/api/todoapp/{todo_id}")
        assert response.status_code == 200
        assert "Todo deleted successfully" in response.json()["message"]
        
        # Verify it's actually deleted
        get_response = client.get(f"/api/todoapp/{todo_id}")
        assert get_response.status_code == 404

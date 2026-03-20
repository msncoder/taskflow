"""
Test suite for Task endpoints.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.features.task.models import Task
from app.features.user.models import User, UserRole


@pytest.mark.asyncio
class TestTaskEndpoints:
    """Test task endpoints."""

    async def test_admin_creates_task(
        self,
        test_client: AsyncClient,
        test_admin_user,
        test_company,
        admin_token: str,
    ):
        """Test admin can create task."""
        response = await test_client.post(
            "/tasks/",
            json={
                "title": "Test Task",
                "description": "Test Description",
                "due_date": "2026-04-01"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["is_completed"] is False
        assert data["created_by"]["email"] == "admin@test.com"

    async def test_admin_creates_task_assigned(
        self,
        test_client: AsyncClient,
        test_admin_user,
        test_employee_user,
        test_company,
        admin_token: str,
    ):
        """Test admin can create task and assign to employee."""
        response = await test_client.post(
            "/tasks/",
            json={
                "title": "Assigned Task",
                "assigned_to_id": str(test_employee_user.id),
                "due_date": "2026-04-01"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["assigned_to_id"] == str(test_employee_user.id)

    async def test_manager_creates_task_assigned_to_employee(
        self,
        test_client: AsyncClient,
        test_manager_user,
        test_employee_user,
        test_company,
        manager_token: str,
    ):
        """Test manager can create task and assign to employee."""
        response = await test_client.post(
            "/tasks/",
            json={
                "title": "Manager Task",
                "assigned_to_id": str(test_employee_user.id)
            },
            headers={"Authorization": f"Bearer {manager_token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["assigned_to_id"] == str(test_employee_user.id)

    async def test_manager_creates_task_assigned_to_manager_forbidden(
        self,
        test_client: AsyncClient,
        test_manager_user,
        test_company,
        manager_token: str,
        db_session,
    ):
        """Test manager cannot assign task to other manager (403)."""
        # Create another manager
        other_manager = User(
            email="othermanager@test.com",
            full_name="Other Manager",
            hashed_password="hashed",
            role=UserRole.MANAGER,
            company_id=test_company.id
        )
        db_session.add(other_manager)
        await db_session.commit()

        response = await test_client.post(
            "/tasks/",
            json={
                "title": "Manager Task",
                "assigned_to_id": str(other_manager.id)
            },
            headers={"Authorization": f"Bearer {manager_token}"}
        )

        assert response.status_code == 403

    async def test_employee_creates_task_forbidden(
        self,
        test_client: AsyncClient,
        test_employee_user,
        test_company,
        employee_token: str,
    ):
        """Test employee cannot create task (403)."""
        response = await test_client.post(
            "/tasks/",
            json={
                "title": "Employee Task"
            },
            headers={"Authorization": f"Bearer {employee_token}"}
        )

        assert response.status_code == 403

    async def test_list_tasks_admin(
        self,
        test_client: AsyncClient,
        test_admin_user,
        test_company,
        admin_token: str,
        db_session,
    ):
        """Test admin can list all company tasks."""
        # Create tasks
        task1 = Task(
            title="Task 1",
            company_id=test_company.id,
            created_by_id=test_admin_user.id
        )
        task2 = Task(
            title="Task 2",
            company_id=test_company.id,
            created_by_id=test_admin_user.id,
            assigned_to_id=test_admin_user.id
        )
        db_session.add_all([task1, task2])
        await db_session.commit()

        response = await test_client.get(
            "/tasks/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2
        assert len(data["tasks"]) >= 2

    async def test_list_tasks_employee(
        self,
        test_client: AsyncClient,
        test_employee_user,
        test_company,
        employee_token: str,
        db_session,
    ):
        """Test employee can only see tasks assigned to them."""
        # Create task assigned to employee
        task = Task(
            title="Assigned Task",
            company_id=test_company.id,
            created_by_id=test_employee_user.id,
            assigned_to_id=test_employee_user.id
        )
        db_session.add(task)
        await db_session.commit()

        response = await test_client.get(
            "/tasks/",
            headers={"Authorization": f"Bearer {employee_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        # Employee should only see their assigned tasks
        assert data["total"] >= 1

    async def test_get_task_detail(
        self,
        test_client: AsyncClient,
        test_admin_user,
        test_company,
        admin_token: str,
        db_session,
    ):
        """Test getting task detail."""
        # Create task
        task = Task(
            title="Detail Task",
            description="Test Description",
            company_id=test_company.id,
            created_by_id=test_admin_user.id
        )
        db_session.add(task)
        await db_session.commit()

        response = await test_client.get(
            f"/tasks/{task.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Detail Task"
        assert "created_by" in data

    async def test_update_task(
        self,
        test_client: AsyncClient,
        test_admin_user,
        test_company,
        admin_token: str,
        db_session,
    ):
        """Test updating task (creator can update)."""
        # Create task
        task = Task(
            title="Original Title",
            company_id=test_company.id,
            created_by_id=test_admin_user.id
        )
        db_session.add(task)
        await db_session.commit()

        response = await test_client.patch(
            f"/tasks/{task.id}",
            json={"title": "Updated Title"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"

    async def test_update_task_not_creator_forbidden(
        self,
        test_client: AsyncClient,
        test_employee_user,
        test_company,
        employee_token: str,
        db_session,
    ):
        """Test non-creator cannot update task (403)."""
        # Create task by different user
        other_user = User(
            email="otheruser@test.com",
            full_name="Other User",
            hashed_password="hashed",
            role=UserRole.EMPLOYEE,
            company_id=test_company.id
        )
        db_session.add(other_user)
        await db_session.commit()

        task = Task(
            title="Admin Task",
            company_id=test_company.id,
            created_by_id=other_user.id
        )
        db_session.add(task)
        await db_session.commit()

        response = await test_client.patch(
            f"/tasks/{task.id}",
            json={"title": "Updated"},
            headers={"Authorization": f"Bearer {employee_token}"}
        )

        assert response.status_code == 403

    async def test_toggle_complete_assigned_employee(
        self,
        test_client: AsyncClient,
        test_employee_user,
        test_company,
        employee_token: str,
        db_session,
    ):
        """Test assigned employee can toggle task completion."""
        # Create task assigned to employee
        task = Task(
            title="Toggle Task",
            company_id=test_company.id,
            created_by_id=test_employee_user.id,
            assigned_to_id=test_employee_user.id,
            is_completed=False
        )
        db_session.add(task)
        await db_session.commit()

        # Toggle complete
        response = await test_client.patch(
            f"/tasks/{task.id}/toggle-complete",
            headers={"Authorization": f"Bearer {employee_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_completed"] is True

        # Toggle back
        response = await test_client.patch(
            f"/tasks/{task.id}/toggle-complete",
            headers={"Authorization": f"Bearer {employee_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_completed"] is False

    async def test_toggle_complete_not_assigned_forbidden(
        self,
        test_client: AsyncClient,
        test_employee_user,
        test_company,
        employee_token: str,
        db_session,
    ):
        """Test employee cannot toggle task not assigned to them (403)."""
        # Create task not assigned to employee
        task = Task(
            title="Other Task",
            company_id=test_company.id,
            created_by_id=test_employee_user.id,
            assigned_to_id=None  # Not assigned
        )
        db_session.add(task)
        await db_session.commit()

        response = await test_client.patch(
            f"/tasks/{task.id}/toggle-complete",
            headers={"Authorization": f"Bearer {employee_token}"}
        )

        assert response.status_code == 403

    async def test_toggle_complete_admin_forbidden(
        self,
        test_client: AsyncClient,
        test_admin_user,
        test_company,
        admin_token: str,
        db_session,
    ):
        """Test admin cannot toggle (must use update) - 403 if not assigned."""
        # Create task not assigned to admin
        task = Task(
            title="Admin Task",
            company_id=test_company.id,
            created_by_id=test_admin_user.id,
            assigned_to_id=None
        )
        db_session.add(task)
        await db_session.commit()

        response = await test_client.patch(
            f"/tasks/{task.id}/toggle-complete",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 403

    async def test_delete_task_admin(
        self,
        test_client: AsyncClient,
        test_admin_user,
        test_company,
        admin_token: str,
        db_session,
    ):
        """Test admin can delete task."""
        # Create task
        task = Task(
            title="Delete Task",
            company_id=test_company.id,
            created_by_id=test_admin_user.id
        )
        db_session.add(task)
        await db_session.commit()

        response = await test_client.delete(
            f"/tasks/{task.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 204

        # Verify deletion
        result = await db_session.execute(
            select(Task).where(Task.id == task.id)
        )
        assert result.scalar_one_or_none() is None

    async def test_delete_task_non_admin_forbidden(
        self,
        test_client: AsyncClient,
        test_employee_user,
        test_company,
        employee_token: str,
        db_session,
    ):
        """Test non-admin cannot delete task (403)."""
        # Create task
        task = Task(
            title="Employee Task",
            company_id=test_company.id,
            created_by_id=test_employee_user.id
        )
        db_session.add(task)
        await db_session.commit()

        response = await test_client.delete(
            f"/tasks/{task.id}",
            headers={"Authorization": f"Bearer {employee_token}"}
        )

        assert response.status_code == 403

    async def test_new_task_default_not_completed(
        self,
        test_client: AsyncClient,
        test_admin_user,
        test_company,
        admin_token: str,
    ):
        """Test new task defaults to is_completed=False."""
        response = await test_client.post(
            "/tasks/",
            json={
                "title": "Default Task"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["is_completed"] is False

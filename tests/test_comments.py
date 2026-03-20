"""
Test suite for Comment endpoints.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.features.comment.models import Comment
from app.features.task.models import Task


@pytest.mark.asyncio
class TestCommentEndpoints:
    """Test comment endpoints."""

    async def test_add_comment(
        self,
        test_client: AsyncClient,
        test_admin_user,
        test_company,
        admin_token: str,
        db_session,
    ):
        """Test adding a comment to a task."""
        # Create a task first
        task = Task(
            title="Test Task",
            description="Test Description",
            company_id=test_company.id,
            created_by_id=test_admin_user.id,
        )
        db_session.add(task)
        await db_session.commit()

        # Add comment
        response = await test_client.post(
            f"/tasks/{task.id}/comments/",
            json={"body": "This is a test comment"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["body"] == "This is a test comment"
        assert "author" in data
        assert data["author"]["email"] == "admin@test.com"

    async def test_list_comments(
        self,
        test_client: AsyncClient,
        test_admin_user,
        test_company,
        admin_token: str,
        db_session,
    ):
        """Test listing comments for a task."""
        # Create a task
        task = Task(
            title="Test Task",
            company_id=test_company.id,
            created_by_id=test_admin_user.id,
        )
        db_session.add(task)
        await db_session.commit()

        # Add comments
        for i in range(3):
            comment = Comment(
                task_id=task.id,
                author_id=test_admin_user.id,
                body=f"Comment {i+1}"
            )
            db_session.add(comment)
        await db_session.commit()

        # List comments
        response = await test_client.get(
            f"/tasks/{task.id}/comments/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "comments" in data
        assert "total" in data
        assert data["total"] == 3
        assert len(data["comments"]) == 3

    async def test_delete_comment_author(
        self,
        test_client: AsyncClient,
        test_admin_user,
        test_company,
        admin_token: str,
        db_session,
    ):
        """Test deleting own comment."""
        # Create a task
        task = Task(
            title="Test Task",
            company_id=test_company.id,
            created_by_id=test_admin_user.id,
        )
        db_session.add(task)
        await db_session.commit()

        # Add comment
        comment = Comment(
            task_id=task.id,
            author_id=test_admin_user.id,
            body="Test comment"
        )
        db_session.add(comment)
        await db_session.commit()

        # Delete comment
        response = await test_client.delete(
            f"/tasks/{task.id}/comments/{comment.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 204

        # Verify deletion
        result = await db_session.execute(
            select(Comment).where(Comment.id == comment.id)
        )
        assert result.scalar_one_or_none() is None

    async def test_delete_comment_not_author(
        self,
        test_client: AsyncClient,
        test_admin_user,
        test_employee_user,
        test_company,
        employee_token: str,
        db_session,
    ):
        """Test deleting someone else's comment returns 403."""
        # Create a task
        task = Task(
            title="Test Task",
            company_id=test_company.id,
            created_by_id=test_admin_user.id,
        )
        db_session.add(task)
        await db_session.commit()

        # Add comment by admin
        comment = Comment(
            task_id=task.id,
            author_id=test_admin_user.id,
            body="Admin comment"
        )
        db_session.add(comment)
        await db_session.commit()

        # Try to delete as employee
        response = await test_client.delete(
            f"/tasks/{task.id}/comments/{comment.id}",
            headers={"Authorization": f"Bearer {employee_token}"}
        )

        assert response.status_code == 403

    async def test_add_comment_no_task_access(
        self,
        test_client: AsyncClient,
        test_employee_user,
        test_company,
        employee_token: str,
        db_session,
    ):
        """Test adding comment to task without access returns 404."""
        # Create a task not assigned to employee
        task = Task(
            title="Test Task",
            company_id=test_company.id,
            created_by_id=test_employee_user.id,
            # Not assigned to employee
            assigned_to_id=None,
        )
        db_session.add(task)
        await db_session.commit()

        # Try to add comment
        response = await test_client.post(
            f"/tasks/{task.id}/comments/",
            json={"body": "Test comment"},
            headers={"Authorization": f"Bearer {employee_token}"}
        )

        assert response.status_code == 404

    async def test_add_comment_empty_body(
        self,
        test_client: AsyncClient,
        test_admin_user,
        test_company,
        admin_token: str,
        db_session,
    ):
        """Test adding comment with empty body returns 422."""
        # Create a task
        task = Task(
            title="Test Task",
            company_id=test_company.id,
            created_by_id=test_admin_user.id,
        )
        db_session.add(task)
        await db_session.commit()

        # Try to add comment with empty body
        response = await test_client.post(
            f"/tasks/{task.id}/comments/",
            json={"body": ""},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 422

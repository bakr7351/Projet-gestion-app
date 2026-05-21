"""
History Service
Encapsulates all business logic related to calculation history.
"""

import logging
from backend.extensions import db
from backend.models.calculation_history import CalculationHistory

logger = logging.getLogger(__name__)


class HistoryService:
    """Service for managing user calculation history."""

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def save_entry(
        self,
        user_id: int,
        calc_type: str,
        input_params: dict,
        result_summary: dict,
        custom_name: str = None,
    ) -> CalculationHistory:
        """Save a new calculation history entry for a user.

        Enforces the per-user limit before inserting, then creates and
        persists a new CalculationHistory record.

        Args:
            user_id: ID of the authenticated user.
            calc_type: One of 'absorption', 'desorption', 'mccabe_thiele'.
            input_params: Dict of input parameters for the calculation.
            result_summary: Dict summarising the calculation results.
            custom_name: Optional human-readable label for the entry.

        Returns:
            The newly created CalculationHistory instance.
        """
        self.enforce_limit(user_id)

        entry = CalculationHistory(
            user_id=user_id,
            calculation_type=calc_type,
            custom_name=custom_name,
        )
        entry.input_params_dict = input_params
        entry.result_summary_dict = result_summary

        db.session.add(entry)
        db.session.commit()
        return entry

    # ------------------------------------------------------------------
    # Limit enforcement
    # ------------------------------------------------------------------

    def enforce_limit(self, user_id: int, max_entries: int = 200) -> None:
        """Delete the oldest entry when the user has reached max_entries.

        Args:
            user_id: ID of the user whose history is being checked.
            max_entries: Maximum number of entries allowed (default 200).
        """
        count = CalculationHistory.query.filter_by(user_id=user_id).count()
        if count >= max_entries:
            oldest = (
                CalculationHistory.query
                .filter_by(user_id=user_id)
                .order_by(CalculationHistory.created_at.asc())
                .first()
            )
            if oldest:
                db.session.delete(oldest)
                db.session.commit()

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_entries(
        self,
        user_id: int,
        calc_type: str = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple:
        """Return a paginated list of history entries for a user.

        Args:
            user_id: ID of the authenticated user (REQUIRED — never
                     returns entries belonging to other users).
            calc_type: Optional filter; when provided only entries whose
                       calculation_type matches are returned.
            page: 1-based page number.
            per_page: Number of entries per page.

        Returns:
            A tuple (entries, total) where *entries* is the list of
            CalculationHistory objects for the requested page and *total*
            is the overall count matching the filters.
        """
        query = CalculationHistory.query.filter_by(user_id=user_id)

        if calc_type is not None:
            query = query.filter_by(calculation_type=calc_type)

        query = query.order_by(CalculationHistory.created_at.desc())

        total = query.count()
        offset = (page - 1) * per_page
        entries = query.offset(offset).limit(per_page).all()

        return entries, total

    def get_entry(self, entry_id: str, user_id: int):
        """Return a single history entry if it exists and belongs to user_id.

        Args:
            entry_id: UUID string of the entry.
            user_id: ID of the requesting user.

        Returns:
            The CalculationHistory instance, or None if not found or if
            the entry belongs to a different user.
        """
        entry = CalculationHistory.query.get(entry_id)
        if entry is None or entry.user_id != user_id:
            return None
        return entry

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete_entry(self, entry_id: str, user_id: int) -> bool:
        """Delete a single history entry.

        Args:
            entry_id: UUID string of the entry to delete.
            user_id: ID of the requesting user.

        Returns:
            True on successful deletion.

        Raises:
            ValueError: If the entry does not exist (404 message).
            PermissionError: If the entry belongs to another user (403 message).
        """
        entry = CalculationHistory.query.get(entry_id)
        if entry is None:
            raise ValueError(f"Entry {entry_id} not found (404)")
        if entry.user_id != user_id:
            raise PermissionError(
                f"Access denied: entry {entry_id} belongs to another user (403)"
            )
        db.session.delete(entry)
        db.session.commit()
        return True

    def delete_all_entries(self, user_id: int) -> int:
        """Delete all history entries for a user.

        Args:
            user_id: ID of the user whose history should be cleared.

        Returns:
            The number of entries that were deleted.
        """
        count = CalculationHistory.query.filter_by(user_id=user_id).count()
        CalculationHistory.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return count

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update_name(
        self, entry_id: str, user_id: int, name: str
    ) -> CalculationHistory:
        """Rename a history entry.

        Args:
            entry_id: UUID string of the entry to rename.
            user_id: ID of the requesting user.
            name: New custom name (must be ≤ 100 characters).

        Returns:
            The updated CalculationHistory instance.

        Raises:
            ValueError: If *name* exceeds 100 characters, or if the
                        entry does not exist (404 message).
            PermissionError: If the entry belongs to another user (403 message).
        """
        if len(name) > 100:
            raise ValueError(
                f"Custom name must not exceed 100 characters (got {len(name)})"
            )

        entry = CalculationHistory.query.get(entry_id)
        if entry is None:
            raise ValueError(f"Entry {entry_id} not found (404)")
        if entry.user_id != user_id:
            raise PermissionError(
                f"Access denied: entry {entry_id} belongs to another user (403)"
            )

        entry.custom_name = name
        db.session.commit()
        return entry


# Module-level singleton — mirrors the pattern used by other services
history_service = HistoryService()

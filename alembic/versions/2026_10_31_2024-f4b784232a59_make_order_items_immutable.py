"""make order_items immutable

Revision ID: f4b784232a59
Revises: 9e5e0c342217
Create Date: 2026-10-31 20:24:48.581042

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f4b784232a59"
down_revision: Union[str, Sequence[str], None] = "9e5e0c342217"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """An order line cannot be changed once written.

    The repository offers no way to update one, but that only binds this
    application. The trigger binds everyone, including a careless UPDATE
    typed into psql, so "the price on this invoice is what was charged" is
    a fact about the database rather than a promise about the code.

    UPDATE only. DELETE is left alone so that deleting an order still
    cascades to its lines; removing a whole order is a different decision
    from rewriting one, and it leaves nothing behind that could mislead.
    """
    op.execute(
        """
        CREATE FUNCTION order_items_are_immutable() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION
                'order_items row % cannot be changed once written', OLD.id
                USING ERRCODE = 'restrict_violation';
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER order_items_no_update
            BEFORE UPDATE ON order_items
            FOR EACH ROW EXECUTE FUNCTION order_items_are_immutable();
        """
    )


def downgrade() -> None:
    """Drop the trigger, then the function it calls."""
    op.execute("DROP TRIGGER order_items_no_update ON order_items;")
    op.execute("DROP FUNCTION order_items_are_immutable();")

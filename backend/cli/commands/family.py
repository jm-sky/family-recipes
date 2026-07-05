"""Family management CLI commands."""

import asyncio

import typer
from rich.console import Console
from rich.table import Table

from ..main import COMMAND_GROUPS, show_group_interactive_menu

family_app = typer.Typer(
    name="family",
    help="Family management commands",
    no_args_is_help=False,  # We handle no-args case ourselves for interactive mode
)

console = Console()


@family_app.callback(invoke_without_command=True)
def family_callback(ctx: typer.Context) -> None:
    """Callback for family command group - shows interactive menu if no subcommand provided."""
    if ctx.invoked_subcommand is None:
        # No subcommand provided, show interactive menu
        show_group_interactive_menu("family", COMMAND_GROUPS["family"])


async def _create_family_async(name: str, owner_email: str) -> None:
    from app.core.database import get_db
    from app.modules.auth.repositories import UserRepository
    from app.modules.family.repository import FamilyRepository
    from app.modules.family.service import FamilyService

    async for db in get_db():
        service = FamilyService(repository=FamilyRepository(db))
        user_repo = UserRepository(db)

        owner = await user_repo.get_user_by_email(owner_email)
        if owner is None:
            console.print(f"[red]User with email {owner_email} not found[/red]")
            raise typer.Exit(1)

        family = await service.create_family(user_id=owner.id, name=name)
        console.print(f"[green]Family created:[/green] {family.name} ({family.id}) plan={family.plan} owner={owner_email}")
        return


async def _set_plan_async(family_id: str, plan: str) -> None:
    from app.core.database import get_db
    from app.modules.family.constants import PLAN_MEMBER_LIMITS
    from app.modules.family.repository import FamilyRepository

    if plan not in PLAN_MEMBER_LIMITS:
        console.print(f"[red]Invalid plan '{plan}'. Valid plans: {', '.join(PLAN_MEMBER_LIMITS)}[/red]")
        raise typer.Exit(1)

    async for db in get_db():
        repo = FamilyRepository(db)
        family = await repo.get_family(family_id)
        if family is None:
            console.print(f"[red]Family {family_id} not found[/red]")
            raise typer.Exit(1)

        family.plan = plan
        await db.commit()
        limit = PLAN_MEMBER_LIMITS[plan]
        console.print(f"[green]Plan updated:[/green] {family.name} -> {plan} (member limit: {limit if limit is not None else 'unlimited'})")
        return


async def _list_families_async() -> None:
    from sqlalchemy import select

    from app.core.database import get_db
    from app.modules.family.db_models import FamilyDB
    from app.modules.family.repository import FamilyRepository

    async for db in get_db():
        repo = FamilyRepository(db)
        result = await db.execute(select(FamilyDB).order_by(FamilyDB.created_at))
        families = list(result.scalars().all())

        table = Table(title="Families", show_lines=True)
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Plan")
        table.add_column("Members")
        table.add_column("Owner ID")
        table.add_column("Created")

        for family in families:
            member_count = await repo.count_members(family.id)
            table.add_row(
                family.id,
                family.name,
                family.plan,
                str(member_count),
                family.owner_id,
                family.created_at.isoformat(),
            )

        console.print(table)
        return


@family_app.command("create")
def create_family(
    name: str = typer.Argument(..., help="Family name"),
    email: str = typer.Option(..., "--owner-email", "-e", prompt=True, help="Owner email"),
) -> None:
    """Create a family and assign the owner."""
    asyncio.run(_create_family_async(name=name, owner_email=email))


@family_app.command("set-plan")
def set_plan(
    family_id: str = typer.Argument(..., help="Family identifier"),
    plan: str = typer.Argument(..., help="Plan: free, basic or pro"),
) -> None:
    """Set the family plan manually (billing is disabled at launch)."""
    asyncio.run(_set_plan_async(family_id=family_id, plan=plan))


@family_app.command("list")
def list_families() -> None:
    """List all families."""
    asyncio.run(_list_families_async())

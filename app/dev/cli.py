import asyncio
import typer

from app.dev.db import (
    create_database,
    drop_database,
    reset_database,
    wipe_database,
)
from app.dev.fake_users import generate_fake_users
from app.dev.match import generate_matches
from app.dev.seed import seed_database

app = typer.Typer()


@app.command()
def create():
    asyncio.run(create_database())


@app.command()
def drop():
    asyncio.run(drop_database())


@app.command()
def reset():
    asyncio.run(reset_database())


@app.command()
def wipe():
    asyncio.run(wipe_database())


@app.command()
def seed():
    asyncio.run(seed_database())


@app.command("fake-users")
def fake_users(
    count: int = 50,
):
    """Generate fake completed users."""
    asyncio.run(generate_fake_users(count))
    
@app.command("match-me")
def match_me(
    telegram_id: int,
    count: int = 20,
    mutual: bool = False,
):
    """
    Generate likes or matches from fake users.
    """

    asyncio.run(
        generate_matches(
            telegram_id,
            count=count,
            mutual=mutual,
        )
    )


if __name__ == "__main__":
    app()

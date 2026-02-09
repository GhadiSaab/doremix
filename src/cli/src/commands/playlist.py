import typer

from rich.console import Console
from rich.table import Table

from src.services.playlist import (
    get_all_playlists,
    get_playlist,
    get_playlist_tracks,
    remove_track,
    create_playlist,
    delete_playlist,
    update_playlist,
    add_track_to_playlist,
    search_playlists,
    search_tracks_in_playlist,
)

app = typer.Typer()
console = Console()


@app.command(help="List all playlists.")
def list():
    try:
        playlists = get_all_playlists()
    except Exception as e:
        print(e)
        return

    table = Table(title="All Playlists")

    table.add_column("id", style="cyan")
    table.add_column("title", style="magenta")

    for playlist in playlists:
        id = str(playlist.idPlaylist)
        title = playlist.name

        table.add_row(id, title)

    console.print(table)


@app.command(help="Get playlist infos.")
def get(id: str):
    try:
        playlist = get_playlist(id)
    except Exception as e:
        print(e)
        return

    table = Table(show_header=False)

    table.add_column("Field", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("id", str(playlist.idPlaylist))
    table.add_row("name", playlist.name)
    table.add_row("vote", str(playlist.vote))
    table.add_row("createdAt", playlist.createdAt.strftime("%B %d %Y"))

    console.print(table)


@app.command(help="List all track from a playlist.")
def tracks(id: str):
    try:
        tracks = get_playlist_tracks(id)
    except Exception as e:
        print(e)
        return

    table = Table(title="All tracks")

    table.add_column("id", style="cyan")
    table.add_column("title", style="magenta")

    for track in tracks:
        id = str(track.idTrack)
        title = track.title
        table.add_row(id, title)

    console.print(table)


@app.command(help="Remove a track from a playlist.")
def remove(playlist_id: str, track_id: str):
    try:
        print(remove_track(playlist_id, track_id))
    except Exception as e:
        print(e)
        return


@app.command(help="Create a new playlist.")
def create(
    name: str = typer.Option(..., "--name", "-n", help="Playlist name"),
    genre: int = typer.Option(
        1,
        "--genre",
        "-g",
        help="Genre ID (1=Sans genre, 2=Rock, 3=Pop, 4=Hip-Hop, 5=Jazz, 6=Electro, 7=Metal, 8=Classical, 9=Reggae)",
    ),
    visibility: str = typer.Option(
        "PUBLIC",
        "--visibility",
        "-v",
        help="Visibility (PUBLIC, PRIVATE, SHARED)",
    ),
    # owner: int = typer.Option(..., "--owner", "-o", help="Owner ID")  # TODO: À supprimer quand l'auth sera en place (récupéré depuis le token)
):
    try:
        playlist = create_playlist(name, genre, visibility)
        # TODO: Quand l'auth sera en place :
        # playlist = create_playlist(name, genre, visibility, current_user.id)

        console.print("[green]✓ Playlist créée avec succès ![/green]")

        table = Table(show_header=False)
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("id", str(playlist.idPlaylist))
        table.add_row("name", playlist.name)
        table.add_row("genre", str(playlist.idGenre))
        table.add_row("visibility", playlist.visibility.value)
        table.add_row("createdAt", playlist.createdAt.strftime("%B %d %Y"))
        table.add_row("updatedAt", playlist.updatedAt.strftime("%B %d %Y"))

        console.print(table)
    except Exception as e:
        console.print(f"[red]✗ Erreur: {e}[/red]")


@app.command(help="Delete a playlist by ID.")
def delete(
    playlist_id: int = typer.Argument(..., help="Playlist ID to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
    # TODO: Quand l'auth sera en place, l'utilisateur sera automatiquement identifié via le token
):
    try:
        playlist = get_playlist(str(playlist_id))

        if not force:
            confirm = typer.confirm(
                f"Do you really want to delete the playlist '{playlist.name}'?"
            )
            if not confirm:
                console.print("[yellow]Deletion cancelled.[/yellow]")
                raise typer.Abort()

        result = delete_playlist(str(playlist_id))
        console.print(f"[green]✓ {result['message']}[/green]")

    except typer.Abort:
        pass
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@app.command(help="Update a playlist by ID.")
def update(
    playlist_id: int = typer.Argument(..., help="Playlist ID to update"),
    name: str = typer.Option(None, "--name", "-n", help="New playlist name"),
    genre: int = typer.Option(
        None,
        "--genre",
        "-g",
        help="New genre ID (1=Sans genre, 2=Rock, 3=Pop, 4=Hip-Hop, 5=Jazz, 6=Electro, 7=Metal, 8=Classical, 9=Reggae)",
    ),
    visibility: str = typer.Option(
        None,
        "--visibility",
        "-v",
        help="New visibility (PUBLIC, PRIVATE, SHARED)",
    ),
    # TODO: Quand l'auth sera en place, l'utilisateur sera automatiquement identifié via le token
):
    try:
        if name is None and genre is None and visibility is None:
            console.print(
                "[yellow]No changes specified. Use --name, --genre, or --visibility.[/yellow]"
            )
            raise typer.Abort()

        updated_playlist = update_playlist(str(playlist_id), name, genre, visibility)

        console.print("[green]✓ Playlist successfully updated![/green]")

        table = Table(show_header=False)
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("id", str(updated_playlist.idPlaylist))
        table.add_row("name", updated_playlist.name)
        table.add_row("genre", str(updated_playlist.idGenre))
        table.add_row("visibility", updated_playlist.visibility.value)
        table.add_row("createdAt", updated_playlist.createdAt.strftime("%B %d %Y"))
        table.add_row("updatedAt", updated_playlist.updatedAt.strftime("%B %d %Y"))

        console.print(table)

    except typer.Abort:
        pass
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@app.command(help="Add a track to a playlist.")
def add_track(
    playlist_id: int = typer.Argument(..., help="Playlist ID"),
    youtube_link: str = typer.Option(
        ..., "--url", "-u", help="YouTube link of the track"
    ),
    title: str = typer.Option(
        ..., "--title", "-t", help="Track title (ignored if track already exists)"
    ),
    # TODO: Quand l'auth sera en place, l'utilisateur sera automatiquement identifié via le token
):
    try:
        track = add_track_to_playlist(str(playlist_id), title, youtube_link)

        console.print(f"[green]✓ Track '{track.title}' successfully added![/green]")

        table = Table(show_header=False)
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="magenta")

        artists = ", ".join([artist.name for artist in track.artists])
        duration = (
            f"{track.durationSeconds // 60}:{track.durationSeconds % 60:02d}"
            if track.durationSeconds
            else "N/A"
        )

        table.add_row("id", str(track.idTrack))
        table.add_row("title", track.title)
        table.add_row("artists", artists)
        table.add_row("duration", duration)
        table.add_row("youtube", track.youtubeLink or "N/A")

        console.print(table)

        playlist = get_playlist(str(playlist_id))
        tracks = get_playlist_tracks(str(playlist_id))

        tracks_table = Table(title=f"All tracks in '{playlist.name}'")
        tracks_table.add_column("id", style="cyan")
        tracks_table.add_column("title", style="magenta")
        tracks_table.add_column("artists", style="blue")

        for t in tracks:
            t_artists = ", ".join([artist.name for artist in t.artists])
            tracks_table.add_row(str(t.idTrack), t.title, t_artists)

        console.print(tracks_table)

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@app.command(help="Search playlists by name.")
def search(
    query: str = typer.Argument(..., help="Search query (partial match on name)"),
):
    try:
        playlists = search_playlists(query)

        if not playlists:
            console.print(f"[yellow]No playlists found matching '{query}'[/yellow]")
            return

        table = Table(title=f"Search results for '{query}'")
        table.add_column("id", style="cyan")
        table.add_column("name", style="magenta")
        table.add_column("genre", style="blue")
        table.add_column("visibility", style="green")
        table.add_column("votes", style="yellow")

        for playlist in playlists:
            table.add_row(
                str(playlist.idPlaylist),
                playlist.name,
                str(playlist.idGenre),
                playlist.visibility.value,
                str(playlist.vote),
            )

        console.print(table)
        console.print(f"\n[green]{len(playlists)} playlist(s) found[/green]")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@app.command(help="Search tracks in a playlist by title.")
def search_tracks(
    playlist_id: int = typer.Argument(..., help="Playlist ID"),
    query: str = typer.Argument(..., help="Search query (partial match on title)"),
):
    try:
        playlist = get_playlist(str(playlist_id))
        tracks = search_tracks_in_playlist(str(playlist_id), query)

        if not tracks:
            console.print(
                f"[yellow]No tracks found matching '{query}' in playlist '{playlist.name}'[/yellow]"
            )
            return

        table = Table(title=f"Search results for '{query}' in '{playlist.name}'")
        table.add_column("id", style="cyan")
        table.add_column("title", style="magenta")
        table.add_column("artists", style="blue")
        table.add_column("duration", style="green")

        for track in tracks:
            artists = ", ".join([artist.name for artist in track.artists])
            duration = (
                f"{track.durationSeconds // 60}:{track.durationSeconds % 60:02d}"
                if track.durationSeconds
                else "N/A"
            )
            table.add_row(str(track.idTrack), track.title, artists, duration)

        console.print(table)
        console.print(f"\n[green]{len(tracks)} track(s) found[/green]")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")

import os
import yt_dlp
import concurrent.futures
import threading
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt
from rich import box
from rich.text import Text
from rich.layout import Layout
import time

console = Console()

def print_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    banner_text = Text()
    banner_text.append("🎵 ", style="bold red")
    banner_text.append("YouTube Playlist Downloader ", style="bold cyan")
    banner_text.append("1.0", style="bold yellow")
    banner_text.append("\n✨ ", style="bold magenta")
    banner_text.append("Created by ", style="bold white")
    banner_text.append("Flonxi", style="bold green")
    
    panel = Panel(
        banner_text,
        box=box.DOUBLE_EDGE,
        style="bold blue",
        padding=(1, 2)
    )
    console.print(panel)
    console.print()

def download_video(url, format_choice, download_path, progress, task):
    try:
        if format_choice == "1":
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
        elif format_choice == "2":
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'ogg',
                }],
            }
        else:
            ydl_opts = {
                'format': 'best[ext=mp4]',
                'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        progress.update(task, advance=1)
        return True
    except Exception as e:
        progress.update(task, advance=1)
        return False

def get_playlist_urls(playlist_url):
    try:
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(playlist_url, download=False)
            return [entry['url'] for entry in result['entries']]
    except Exception as e:
        console.print(f"[red]Error getting playlist URLs: {str(e)}[/red]")
        return []

def main():
    print_banner()
    
    playlist_url = Prompt.ask("🎬 [cyan]Enter YouTube playlist URL[/cyan]")
    download_path = Prompt.ask("📁 [cyan]Enter download directory path[/cyan]")
    
    console.print("\n🎵 [yellow]Select format:[/yellow]")
    console.print("  [green]1. MP3 (Audio)[/green]")
    console.print("  [green]2. OGG (Audio)[/green]")
    console.print("  [green]3. MP4 (Video)[/green]")
    format_choice = Prompt.ask("🔢 [cyan]Enter choice[/cyan]", choices=["1", "2", "3"], default="1")
    
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    
    with console.status("[bold green]Getting playlist information...", spinner="dots"):
        urls = get_playlist_urls(playlist_url)
    
    if not urls:
        console.print("[red]❌ Failed to get playlist URLs[/red]")
        return
    
    total_videos = len(urls)
    console.print(f"[green]✅ Found [bold]{total_videos}[/bold] videos in playlist[/green]")
    
    max_threads = min(total_videos, 20)
    
    console.print(f"[cyan]🚀 Using [bold]{max_threads}[/bold] threads for downloading...[/cyan]")
    
    completed = 0
    failed = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        
        main_task = progress.add_task("[cyan]Downloading playlist...", total=total_videos)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            future_to_url = {
                executor.submit(download_video, url, format_choice, download_path, progress, main_task): url 
                for i, url in enumerate(urls)
            }
            
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    if result:
                        completed += 1
                    else:
                        failed += 1
                except Exception as exc:
                    failed += 1
    
    console.print()
    success_panel = Panel(
        f"[green]✅ Successfully downloaded: [bold]{completed}[/bold] videos\n"
        f"[red]❌ Failed downloads: [bold]{failed}[/bold] videos\n"
        f"[blue]📁 Saved to: [bold]{download_path}[/bold]",
        title="🎉 Download Complete!",
        style="bold green",
        box=box.ROUNDED
    )
    console.print(success_panel)

if __name__ == "__main__":
    main()
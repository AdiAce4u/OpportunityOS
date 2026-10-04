import argparse
import sys
import io

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from rich.console import Console
from rich.table import Table
from searcher import JobSearcher
from export_html import generate_html_dashboard
from config import ROLE_CATEGORIES, DEFAULT_SETTINGS

console = Console(force_terminal=True, legacy_windows=False)

def display_summary_table(jobs, sort_by="match"):
    if not jobs:
        console.print("[yellow]No jobs to display.[/yellow]")
        return

    title_suffix = "Ranked by Master CV Project Match %" if sort_by == "match" else ("Ranked by Highest Stipend / Salary" if sort_by == "salary" else "Ranked by Recency")
    table = Table(title=f"✨ Job Discoveries ({title_suffix}) ✨", show_lines=True)
    table.add_column("Match %", style="bold green", justify="center", no_wrap=True)
    table.add_column("Top Matching Project", style="italic cyan")
    table.add_column("Title & Company", style="bold white")
    table.add_column("Stipend / Salary", style="bold yellow")
    table.add_column("Portal", style="magenta")
    table.add_column("Job URL", style="blue")

    for j in jobs[:25]:  # Display top 25 in terminal
        match_str = f"{j.get('match_score', 0):.0f}%"
        best_proj = str(j.get("best_matching_project", "N/A"))[:35]
        title_comp = f"{str(j.get('title', ''))[:30]}\n[dim]{str(j.get('company', ''))[:25]}[/dim]"
        salary = str(j.get("display_salary", "Not Disclosed"))
        
        table.add_row(
            match_str,
            best_proj,
            title_comp,
            salary,
            str(j.get("site", "linkedin")).capitalize(),
            str(j.get("job_url", ""))
        )

    console.print(table)
    if len(jobs) > 25:
        console.print(f"[italic]...and {len(jobs) - 25} more jobs saved to database and dashboard.[/italic]")

def main():
    parser = argparse.ArgumentParser(
        description="Autonomous Multi-Platform Job Search & CV Project Matcher (LinkedIn, Indeed, Glassdoor, Wellfound)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app.py --category sde --location India --sort match
  python app.py --category finance --location Mumbai --sort salary
  python app.py --query "Machine Learning Engineer" --sites linkedin indeed wellfound
  python app.py --all --location India --count 5
        """
    )

    parser.add_argument("-c", "--category", choices=list(ROLE_CATEGORIES.keys()) + ["all"],
                        help="Pre-configured category: sde, data, core, finance, or all")
    parser.add_argument("-q", "--query", type=str,
                        help="Custom job search query (e.g. 'Golang Backend Engineer')")
    parser.add_argument("-l", "--location", type=str, default=DEFAULT_SETTINGS["default_location"],
                        help=f"Target location (default: '{DEFAULT_SETTINGS['default_location']}')")
    parser.add_argument("-n", "--count", type=int, default=DEFAULT_SETTINGS["results_per_role"],
                        help=f"Number of jobs per role (default: {DEFAULT_SETTINGS['results_per_role']})")
    parser.add_argument("--hours", type=int, default=DEFAULT_SETTINGS["hours_old"],
                        help=f"Posted in last N hours (default: {DEFAULT_SETTINGS['hours_old']}h)")
    parser.add_argument("--sites", nargs="+", default=DEFAULT_SETTINGS["sites"],
                        help="Sites to search: linkedin, indeed, glassdoor, zip_recruiter, wellfound (default: linkedin indeed glassdoor)")
    parser.add_argument("--sort", choices=["match", "salary", "recent"], default=DEFAULT_SETTINGS["default_sort"],
                        help="Sort priority: 'match' (CV project similarity), 'salary' (highest stipend), 'recent'")
    parser.add_argument("--cv", type=str, default=DEFAULT_SETTINGS["default_cv_path"],
                        help=f"Path to your Master CV markdown file (default: '{DEFAULT_SETTINGS['default_cv_path']}')")
    parser.add_argument("--all", action="store_true",
                        help="Run search for all categories (sde, data, core, finance)")
    parser.add_argument("--remote", action="store_true",
                        help="Filter strictly for remote jobs")

    args = parser.parse_args()

    searcher = JobSearcher(cv_path=args.cv)

    console.print("[bold blue]========================================================================[/bold blue]")
    console.print("[bold cyan]   🎯 Autonomous Job Matcher: LinkedIn • Indeed • Glassdoor • Wellfound   [/bold cyan]")
    console.print(f"[dim]   Loaded Master CV: {args.cv} ({len(searcher.matcher.projects)} projects identified)[/dim]")
    console.print(f"[dim]   Primary Ranking: {args.sort.upper()} (Similarity with Master CV Projects)[/dim]")
    console.print("[bold blue]========================================================================[/bold blue]\n")

    if args.all or args.category == "all":
        console.print(f"[bold green]Starting comprehensive search across ALL categories in '{args.location}'...[/bold green]\n")
        searcher.search_all_categories(
            location=args.location,
            results_per_role=args.count,
            hours_old=args.hours,
            sites=args.sites
        )
    elif args.category:
        console.print(f"[bold green]Searching category '[{args.category.upper()}]' on portals {args.sites}...[/bold green]\n")
        searcher.search_category(
            category=args.category,
            location=args.location,
            results_per_role=args.count,
            hours_old=args.hours,
            sites=args.sites
        )
    elif args.query:
        console.print(f"[bold green]Searching query '{args.query}' in '{args.location}'...[/bold green]\n")
        searcher.search(
            search_term=args.query,
            location=args.location,
            category="custom",
            results_wanted=args.count,
            hours_old=args.hours,
            sites=args.sites,
            is_remote=args.remote
        )
    else:
        console.print("[yellow]No search arguments provided. Running quick multi-category discovery (SDE, Data, Core, Finance)...[/yellow]")
        console.print("[dim]Tip: Run 'python app.py --help' to see all flags.[/dim]\n")
        searcher.search_all_categories(
            location=args.location,
            results_per_role=2,
            hours_old=args.hours,
            sites=args.sites
        )

    # Generate Dashboard and display table
    dashboard_path = generate_html_dashboard(cv_path=args.cv, sort_by=args.sort)
    all_jobs = searcher.db.get_all_jobs(sort_by=args.sort)
    
    console.print("\n")
    display_summary_table(all_jobs, sort_by=args.sort)

    console.print("\n[bold green]>>> Job Search & Matching Complete![/bold green]")
    console.print(f"[bold white]Interactive Web Dashboard:[/bold white] [underline blue]file:///{dashboard_path.replace(chr(92), '/')}[/underline blue]")
    console.print(f"[bold white]CSV Export:[/bold white] results/jobs_latest.csv")
    console.print(f"[bold white]JSON Export:[/bold white] results/jobs_latest.json")
    console.print(f"[bold white]SQLite DB:[/bold white] jobs_database.db")

if __name__ == "__main__":
    main()

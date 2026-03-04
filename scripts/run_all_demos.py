#!/usr/bin/env python3
"""
HelioTheAnalyst Portfolio Monorepo - Run All Demos

Runs all project demos in sequence (mock mode - no credentials needed).

Usage:
    python scripts/run_all_demos.py
    python scripts/run_all_demos.py --parallel
    python scripts/run_all_demos.py --projects shopify,helioscraper

Options:
    --parallel      Run demos in parallel (faster, but harder to read)
    --projects      Comma-separated list of projects to run
    --verbose       Show detailed output
    --skip-setup    Skip virtual environment checks
"""

import argparse
import asyncio
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional


class Color:
    """ANSI color codes for terminal output."""
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    CYAN = "\033[0;36m"
    MAGENTA = "\033[0;35m"
    BOLD = "\033[1m"
    NC = "\033[0m"  # No Color


class Status(Enum):
    """Demo execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class DemoResult:
    """Result of a demo execution."""
    project: str
    status: Status
    duration: float = 0.0
    output: str = ""
    error: str = ""


# Project configurations
PROJECTS = {
    "shopify-integration-system": {
        "name": "Shopify Integration System",
        "description": "E-commerce sync platform",
        "demo_script": "scripts/run_demo.py",
        "requires_services": ["postgres", "redis"],
    },
    "helioscraper": {
        "name": "HelioScraper",
        "description": "Web scraping framework",
        "demo_script": "scripts/run_demo.py",
        "requires_services": [],
    },
    "order-processing-automation": {
        "name": "Order Processing Automation",
        "description": "Async order pipeline",
        "demo_script": "scripts/run_demo.py",
        "requires_services": ["postgres", "redis"],
    },
    "api-docs-testing-framework": {
        "name": "API Docs & Testing Framework",
        "description": "FastAPI with testing",
        "demo_script": "scripts/run_demo.py",
        "requires_services": [],
    },
    "data-analysis-visualization-suite": {
        "name": "Data Analysis & Visualization Suite",
        "description": "Analytics toolkit (batch mode)",
        "demo_script": "scripts/run_demo.py",
        "requires_services": [],
        "note": "Interactive UI: streamlit run src/app.py",
    },
    "digital-inventory-management": {
        "name": "Digital Inventory Management",
        "description": "Desktop inventory system (CLI mode)",
        "demo_script": "scripts/run_demo.py",
        "requires_services": [],
        "note": "Interactive GUI: python src/main.py",
    },
}


def print_header(text: str) -> None:
    """Print a formatted header."""
    width = 60
    print(f"\n{Color.CYAN}{'=' * width}{Color.NC}")
    print(f"{Color.CYAN}{text.center(width)}{Color.NC}")
    print(f"{Color.CYAN}{'=' * width}{Color.NC}\n")


def print_section(text: str) -> None:
    """Print a section header."""
    print(f"\n{Color.BOLD}{text}{Color.NC}")
    print(f"{Color.BLUE}{'-' * len(text)}{Color.NC}")


def print_info(text: str) -> None:
    """Print an info message."""
    print(f"{Color.BLUE}[INFO]{Color.NC} {text}")


def print_success(text: str) -> None:
    """Print a success message."""
    print(f"{Color.GREEN}[SUCCESS]{Color.NC} {text}")


def print_warning(text: str) -> None:
    """Print a warning message."""
    print(f"{Color.YELLOW}[WARN]{Color.NC} {text}")


def print_error(text: str) -> None:
    """Print an error message."""
    print(f"{Color.RED}[ERROR]{Color.NC} {text}")


def check_venv(project_dir: Path) -> bool:
    """Check if virtual environment exists for a project."""
    venv_paths = [
        project_dir / ".venv",
        project_dir / "venv",
    ]
    return any(v.exists() for v in venv_paths)


def get_python_executable(project_dir: Path) -> Optional[Path]:
    """Get the Python executable path for a project."""
    venv_paths = [
        project_dir / ".venv" / "bin" / "python",
        project_dir / ".venv" / "Scripts" / "python.exe",
        project_dir / "venv" / "bin" / "python",
        project_dir / "venv" / "Scripts" / "python.exe",
    ]
    for path in venv_paths:
        if path.exists():
            return path
    return None


def run_demo(project: str, verbose: bool = False) -> DemoResult:
    """Run a single project demo."""
    import time
    
    config = PROJECTS[project]
    project_dir = Path("projects") / project
    demo_script = project_dir / config["demo_script"]
    
    result = DemoResult(project=project, status=Status.RUNNING)
    start_time = time.time()
    
    # Check if project directory exists
    if not project_dir.exists():
        result.status = Status.SKIPPED
        result.error = f"Project directory not found: {project_dir}"
        result.duration = time.time() - start_time
        return result
    
    # Check if demo script exists
    if not demo_script.exists():
        result.status = Status.SKIPPED
        result.error = f"Demo script not found: {demo_script}"
        result.duration = time.time() - start_time
        return result
    
    # Check virtual environment
    python_exe = get_python_executable(project_dir)
    if not python_exe:
        result.status = Status.SKIPPED
        result.error = "Virtual environment not found. Run: make setup"
        result.duration = time.time() - start_time
        return result
    
    try:
        # Run the demo
        cmd = [str(python_exe), str(demo_script)]
        
        if verbose:
            process = subprocess.run(
                cmd,
                cwd=project_dir,
                capture_output=False,
                text=True,
            )
        else:
            process = subprocess.run(
                cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
            )
            result.output = process.stdout
            result.error = process.stderr
        
        result.duration = time.time() - start_time
        
        if process.returncode == 0:
            result.status = Status.SUCCESS
        else:
            result.status = Status.FAILED
            
    except Exception as e:
        result.status = Status.FAILED
        result.error = str(e)
        result.duration = time.time() - start_time
    
    return result


def print_result(result: DemoResult) -> None:
    """Print a demo result."""
    config = PROJECTS[result.project]
    name = config["name"]
    duration = f"{result.duration:.1f}s"
    
    if result.status == Status.SUCCESS:
        print_success(f"{name} ({duration})")
    elif result.status == Status.FAILED:
        print_error(f"{name} ({duration})")
        if result.error:
            print(f"  {Color.RED}Error: {result.error[:200]}{Color.NC}")
    elif result.status == Status.SKIPPED:
        print_warning(f"{name} - SKIPPED")
        if result.error:
            print(f"  {Color.YELLOW}Reason: {result.error}{Color.NC}")


def print_summary(results: List[DemoResult]) -> None:
    """Print a summary of all demo results."""
    print_header("Demo Summary")
    
    success = sum(1 for r in results if r.status == Status.SUCCESS)
    failed = sum(1 for r in results if r.status == Status.FAILED)
    skipped = sum(1 for r in results if r.status == Status.SKIPPED)
    total_duration = sum(r.duration for r in results)
    
    for result in results:
        config = PROJECTS[result.project]
        name = config["name"]
        duration = f"{result.duration:.1f}s"
        
        if result.status == Status.SUCCESS:
            symbol = f"{Color.GREEN}✓{Color.NC}"
        elif result.status == Status.FAILED:
            symbol = f"{Color.RED}✗{Color.NC}"
        else:
            symbol = f"{Color.YELLOW}○{Color.NC}"
        
        print(f"  {symbol} {name:<40} {duration:>8}")
    
    print(f"\n{Color.BOLD}Results:{Color.NC}")
    print(f"  {Color.GREEN}✓{Color.NC} Success: {success}")
    print(f"  {Color.RED}✗{Color.NC} Failed: {failed}")
    print(f"  {Color.YELLOW}○{Color.NC} Skipped: {skipped}")
    print(f"  {Color.CYAN}⏱{Color.NC} Total time: {total_duration:.1f}s")


def print_interactive_demos() -> None:
    """Print information about interactive demos."""
    print_section("Interactive Demos (Run Separately)")
    print()
    print(f"  {Color.CYAN}Data Analysis Suite (Streamlit):{Color.NC}")
    print("    cd projects/data-analysis-visualization-suite")
    print("    streamlit run src/app.py")
    print()
    print(f"  {Color.CYAN}Inventory Management (GUI):{Color.NC}")
    print("    cd projects/digital-inventory-management")
    print("    python src/main.py")
    print()
    print(f"  {Color.CYAN}API Testing Framework (FastAPI):{Color.NC}")
    print("    cd projects/api-docs-testing-framework")
    print("    uvicorn api_testing.main:app --reload")
    print("    open http://localhost:8000/docs")


def run_sequential(projects: List[str], verbose: bool = False) -> List[DemoResult]:
    """Run demos sequentially."""
    results = []
    
    for project in projects:
        config = PROJECTS[project]
        print_section(f"Running: {config['name']}")
        print_info(f"Description: {config['description']}")
        
        if config.get('note'):
            print_info(f"Note: {config['note']}")
        
        result = run_demo(project, verbose)
        print_result(result)
        results.append(result)
    
    return results


def run_parallel(projects: List[str], verbose: bool = False) -> List[DemoResult]:
    """Run demos in parallel."""
    results = []
    
    print_info(f"Running {len(projects)} demos in parallel...")
    print()
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_project = {
            executor.submit(run_demo, project, verbose): project
            for project in projects
        }
        
        for future in as_completed(future_to_project):
            project = future_to_project[future]
            try:
                result = future.result()
            except Exception as e:
                result = DemoResult(
                    project=project,
                    status=Status.FAILED,
                    error=str(e)
                )
            
            config = PROJECTS[project]
            print_result(result)
            results.append(result)
    
    # Sort results by project order
    project_order = {p: i for i, p in enumerate(projects)}
    results.sort(key=lambda r: project_order[r.project])
    
    return results


def check_docker_services() -> bool:
    """Check if required Docker services are running."""
    try:
        result = subprocess.run(
            ["docker", "compose", "ps", "--services", "--filter", "status=running"],
            capture_output=True,
            text=True,
            cwd="."
        )
        running_services = result.stdout.strip().split("\n")
        
        required = ["postgres", "redis"]
        missing = [s for s in required if s not in running_services]
        
        if missing:
            print_warning(f"Some services not running: {', '.join(missing)}")
            print_info("Start services with: docker-compose up -d")
            return False
        
        return True
    except Exception:
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run all portfolio project demos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_all_demos.py
  python scripts/run_all_demos.py --parallel
  python scripts/run_all_demos.py --projects shopify,helioscraper
  python scripts/run_all_demos.py --verbose
        """
    )
    
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run demos in parallel (faster, but harder to read)"
    )
    parser.add_argument(
        "--projects",
        type=str,
        help="Comma-separated list of projects to run (default: all)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output from each demo"
    )
    parser.add_argument(
        "--skip-services-check",
        action="store_true",
        help="Skip Docker services check"
    )
    
    args = parser.parse_args()
    
    # Print header
    print_header("HelioTheAnalyst Portfolio - Running All Demos")
    print_info("All demos run in MOCK mode (no real credentials needed)")
    print()
    
    # Determine which projects to run
    if args.projects:
        project_list = [p.strip() for p in args.projects.split(",")]
        # Validate project names
        invalid = [p for p in project_list if p not in PROJECTS]
        if invalid:
            print_error(f"Invalid project names: {', '.join(invalid)}")
            print_info(f"Valid projects: {', '.join(PROJECTS.keys())}")
            sys.exit(1)
    else:
        project_list = list(PROJECTS.keys())
    
    print_info(f"Running {len(project_list)} projects: {', '.join(project_list)}")
    print()
    
    # Check Docker services
    if not args.skip_services_check:
        services_ok = check_docker_services()
        if not services_ok:
            print_warning("Some demos may fail without required services")
            print()
    
    # Run demos
    if args.parallel:
        results = run_parallel(project_list, args.verbose)
    else:
        results = run_sequential(project_list, args.verbose)
    
    # Print summary
    print_summary(results)
    
    # Print interactive demos info
    print_interactive_demos()
    
    # Exit with appropriate code
    failed = sum(1 for r in results if r.status == Status.FAILED)
    if failed > 0:
        print()
        print_error(f"{failed} demo(s) failed")
        sys.exit(1)
    else:
        print()
        print_success("All demos completed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()

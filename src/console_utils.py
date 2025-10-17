#!/usr/bin/env python3


class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    CYAN = "\033[0;36m"
    BOLD = "\033[1m"
    NC = "\033[0m"


def print_header(title, emoji="🔧"):
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════════════════════════╗")
    print(f"║{title.center(78, ' ')}║")
    print("╚════════════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.NC}")


def print_section_separator():
    print(f"\n{Colors.BLUE}{'='*80}{Colors.NC}")


def print_success_box(title):
    print(f"\n{Colors.GREEN}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════════════════════════╗")
    print(f"║{title.center(78, ' ')}║")
    print("╚════════════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.NC}")

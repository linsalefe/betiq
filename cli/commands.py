import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from src.agents.betting_agent import BettingAgent
from dotenv import load_dotenv

load_dotenv()
console = Console()

def cmd_today(bankroll: float = 100):
    """Mostra oportunidades de hoje"""
    agent = BettingAgent(current_bankroll=bankroll)
    opportunities = agent.analyze_today_opportunities()
    
    if opportunities:
        report = agent.get_full_report(opportunities)
        console.print(report)
    else:
        console.print("[yellow]⚠️  Nenhuma oportunidade encontrada.[/yellow]")

def cmd_stats(bankroll: float = 100):
    """Mostra estatísticas"""
    agent = BettingAgent(current_bankroll=bankroll)
    stats = agent.get_statistics()
    
    if stats['total_bets'] == 0:
        console.print("[yellow]⚠️  Nenhuma aposta registrada.[/yellow]")
        return
    
    console.print(f"\n📊 [bold]ESTATÍSTICAS[/bold]")
    console.print(f"Total: {stats['total_bets']} apostas")
    console.print(f"Win Rate: {stats['win_rate']:.1f}%")
    console.print(f"ROI: {stats['roi']:.2f}%")
    console.print(f"Lucro: R$ {stats['total_profit']:.2f}\n")

def cmd_history(bankroll: float = 100, n: int = 10):
    """Mostra histórico"""
    agent = BettingAgent(current_bankroll=bankroll)
    bets = agent.bet_history.get_recent_bets(n)
    
    if not bets:
        console.print("[yellow]⚠️  Nenhuma aposta registrada.[/yellow]")
        return
    
    console.print(f"\n📋 [bold]ÚLTIMAS {len(bets)} APOSTAS[/bold]\n")
    for bet in bets:
        status = {'won': '✅', 'lost': '❌', 'void': '⚪', 'pending': '⏳'}.get(bet['status'], '❓')
        profit = f"R$ {bet['profit']:.2f}" if bet['profit'] else "Pendente"
        console.print(f"{status} {bet['match'][:30]} - {bet['market']} @ {bet['odds']} - {profit}")
    console.print("")

def cmd_help():
    """Mostra ajuda"""
    console.print("\n[bold cyan]🤖 AGENTE DE VALUE BETTING - COMANDOS[/bold cyan]\n")
    console.print("[bold]Uso:[/bold] python cli/main.py [comando] [opções]\n")
    console.print("[bold]Comandos disponíveis:[/bold]")
    console.print("  today              Mostra oportunidades de hoje")
    console.print("  stats              Mostra estatísticas")
    console.print("  history [n]        Mostra últimas N apostas (padrão: 10)")
    console.print("  help               Mostra esta ajuda\n")
    console.print("[bold]Exemplos:[/bold]")
    console.print("  python cli/main.py today")
    console.print("  python cli/main.py stats")
    console.print("  python cli/main.py history 20\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        console.print("[yellow]Use: python cli/commands.py [comando][/yellow]")
        console.print("[dim]Execute 'python cli/commands.py help' para ver comandos[/dim]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "today":
        cmd_today()
    elif command == "stats":
        cmd_stats()
    elif command == "history":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        cmd_history(n=n)
    elif command == "help":
        cmd_help()
    else:
        console.print(f"[red]❌ Comando desconhecido: {command}[/red]")
        console.print("[dim]Execute 'python cli/commands.py help' para ver comandos[/dim]")
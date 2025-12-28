import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from src.agents.betting_agent import BettingAgent
from dotenv import load_dotenv

load_dotenv()

console = Console()

def clear_screen():
    os.system('clear' if os.name != 'nt' else 'cls')

def show_menu():
    """Exibe menu principal"""
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]🤖 AGENTE DE VALUE BETTING[/bold cyan]\n"
        "[dim]Sistema de apostas esportivas com análise de valor[/dim]",
        border_style="cyan"
    ))
    
    console.print("\n[bold]MENU PRINCIPAL:[/bold]")
    console.print("1. 📊 Ver oportunidades de hoje")
    console.print("2. ✅ Registrar resultado de aposta")
    console.print("3. 📈 Ver estatísticas")
    console.print("4. 📋 Ver histórico de apostas")
    console.print("5. 🔄 Forçar transição de fase")
    console.print("6. 📁 Exportar dados")
    console.print("7. 🧪 Limpar cache Redis")
    console.print("0. ❌ Sair")
    console.print("")

def view_opportunities():
    """Opção 1: Ver oportunidades"""
    clear_screen()
    console.print("\n[bold cyan]📊 BUSCANDO OPORTUNIDADES...[/bold cyan]\n")
    
    # Pede banca atual
    bankroll = Prompt.ask("💰 Informe sua banca atual (R$)", default="100")
    
    try:
        bankroll = float(bankroll)
    except:
        console.print("[red]❌ Valor inválido![/red]")
        return
    
    agent = BettingAgent(current_bankroll=bankroll)
    opportunities = agent.analyze_today_opportunities()
    
    if not opportunities:
        console.print("\n[yellow]⚠️  Nenhuma oportunidade encontrada hoje.[/yellow]")
        return
    
    # Mostra relatório completo
    report = agent.get_full_report(opportunities)
    console.print(report)
    
    # Pergunta se quer registrar alguma aposta
    if Confirm.ask("\n💾 Deseja registrar alguma aposta?"):
        register_bet_from_opportunities(agent, opportunities)

def register_bet_from_opportunities(agent, opportunities):
    """Registra aposta das oportunidades"""
    console.print("\n[bold]Oportunidades disponíveis:[/bold]")
    for i, opp in enumerate(opportunities, 1):
        console.print(f"{i}. {opp['match']} - {opp['market']} @ {opp['odds']}")
    
    choice = Prompt.ask("Qual aposta deseja registrar? (número)", default="0")
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(opportunities):
            bet = opportunities[idx]
            bet_id = agent.register_bet(bet)
            console.print(f"\n[green]✅ Aposta registrada: {bet_id}[/green]")
        else:
            console.print("[red]❌ Número inválido![/red]")
    except:
        console.print("[red]❌ Entrada inválida![/red]")

def register_result():
    """Opção 2: Registrar resultado"""
    clear_screen()
    console.print("\n[bold cyan]✅ REGISTRAR RESULTADO[/bold cyan]\n")
    
    bankroll = float(Prompt.ask("💰 Banca atual (R$)", default="100"))
    agent = BettingAgent(current_bankroll=bankroll)
    
    # Mostra apostas pendentes
    pending = agent.bet_history.get_pending_bets()
    
    if not pending:
        console.print("[yellow]⚠️  Nenhuma aposta pendente.[/yellow]")
        return
    
    console.print("\n[bold]Apostas pendentes:[/bold]")
    for i, bet in enumerate(pending, 1):
        console.print(f"{i}. {bet['match']} - {bet['market']} @ {bet['odds']} (R$ {bet['stake']})")
    
    choice = Prompt.ask("\nQual aposta finalizar? (número)", default="0")
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(pending):
            bet = pending[idx]
            result = Prompt.ask(
                "Resultado? (won/lost/void)",
                choices=["won", "lost", "void"]
            )
            
            agent.update_bet_result(bet['bet_id'], result)
            console.print(f"\n[green]✅ Resultado registrado: {result.upper()}[/green]")
        else:
            console.print("[red]❌ Número inválido![/red]")
    except:
        console.print("[red]❌ Entrada inválida![/red]")

def view_statistics():
    """Opção 3: Ver estatísticas"""
    clear_screen()
    console.print("\n[bold cyan]📈 ESTATÍSTICAS[/bold cyan]\n")
    
    bankroll = float(Prompt.ask("💰 Banca atual (R$)", default="100"))
    agent = BettingAgent(current_bankroll=bankroll)
    
    stats = agent.get_statistics()
    
    if stats['total_bets'] == 0:
        console.print("[yellow]⚠️  Nenhuma aposta registrada ainda.[/yellow]")
        return
    
    # Cria tabela
    table = Table(title="Estatísticas Gerais")
    table.add_column("Métrica", style="cyan")
    table.add_column("Valor", style="green")
    
    table.add_row("Total de Apostas", str(stats['total_bets']))
    table.add_row("Vitórias", f"{stats['won']} ({stats['win_rate']:.1f}%)")
    table.add_row("Derrotas", str(stats['lost']))
    table.add_row("Anuladas", str(stats['void']))
    table.add_row("Total Apostado", f"R$ {stats['total_staked']:.2f}")
    table.add_row("Lucro/Prejuízo", f"R$ {stats['total_profit']:.2f}")
    table.add_row("ROI", f"{stats['roi']:.2f}%")
    table.add_row("Odd Média", f"{stats['avg_odds']:.2f}")
    
    console.print(table)

def view_history():
    """Opção 4: Ver histórico"""
    clear_screen()
    console.print("\n[bold cyan]📋 HISTÓRICO DE APOSTAS[/bold cyan]\n")
    
    bankroll = float(Prompt.ask("💰 Banca atual (R$)", default="100"))
    agent = BettingAgent(current_bankroll=bankroll)
    
    n = int(Prompt.ask("Quantas apostas mostrar?", default="10"))
    bets = agent.bet_history.get_recent_bets(n)
    
    if not bets:
        console.print("[yellow]⚠️  Nenhuma aposta registrada.[/yellow]")
        return
    
    table = Table(title=f"Últimas {len(bets)} Apostas")
    table.add_column("Data", style="cyan")
    table.add_column("Jogo", style="white")
    table.add_column("Mercado", style="yellow")
    table.add_column("Odd", style="green")
    table.add_column("Stake", style="blue")
    table.add_column("Status", style="magenta")
    table.add_column("Resultado", style="red")
    
    for bet in bets:
        status_emoji = {
            'pending': '⏳',
            'won': '✅',
            'lost': '❌',
            'void': '⚪'
        }.get(bet['status'], '❓')
        
        profit = f"R$ {bet['profit']:.2f}" if bet['profit'] is not None else "-"
        
        # Converte timestamp para string
        timestamp_str = str(bet['timestamp'])[:10] if bet['timestamp'] else "-"
        
        table.add_row(
            timestamp_str,
            bet['match'][:30],
            bet['market'],
            str(bet['odds']),
            f"R$ {bet['stake']:.2f}",
            f"{status_emoji} {bet['status']}",
            profit
        )
    
    console.print(table)

def clear_cache():
    """Opção 7: Limpar cache"""
    clear_screen()
    console.print("\n[bold cyan]🗑️  LIMPAR CACHE REDIS[/bold cyan]\n")
    
    if Confirm.ask("⚠️  Confirma limpeza do cache?"):
        from src.cache.redis_client import RedisCache
        cache = RedisCache()
        cache.clear_all()
        console.print("\n[green]✅ Cache limpo com sucesso![/green]")
    else:
        console.print("\n[yellow]❌ Operação cancelada.[/yellow]")

def main():
    """Loop principal"""
    while True:
        show_menu()
        choice = Prompt.ask("Escolha uma opção", default="0")
        
        if choice == "1":
            view_opportunities()
        elif choice == "2":
            register_result()
        elif choice == "3":
            view_statistics()
        elif choice == "4":
            view_history()
        elif choice == "5":
            console.print("[yellow]⚠️  Função em desenvolvimento...[/yellow]")
        elif choice == "6":
            console.print("[yellow]⚠️  Função em desenvolvimento...[/yellow]")
        elif choice == "7":
            clear_cache()
        elif choice == "0":
            console.print("\n[cyan]👋 Até logo![/cyan]\n")
            break
        else:
            console.print("[red]❌ Opção inválida![/red]")
        
        input("\nPressione ENTER para continuar...")
        clear_screen()

if __name__ == "__main__":
    main()
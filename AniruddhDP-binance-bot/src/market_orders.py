import argparse
from typing import Dict, Optional
from binance import Client
from client import BinanceClient, logging
from binance.exceptions import BinanceAPIException

#CLI Imports
from rich.console import Console
from rich.table import Table
from pyfiglet import Figlet

# Initialize the rich console 
console = Console()

def show_welcome_banner():
    """Displays a cool ASCII art banner for the bot."""
    banner = Figlet(font='slant')
    console.print(f"[bold cyan]{banner.renderText('Futures Bot')}[/bold cyan]")
    console.print("--- [yellow]A CLI-Based Trading Bot for Binance USDT-M Futures[/yellow] ---", justify="center")
    console.print()

def place_market_order(client: Client, symbol: str, side: str, quantity: float) -> Optional[Dict]:
    """
    Places a market order and displays the result in a formatted table.

    Args:
        client: An initialized Binance client instance.
        symbol: The trading symbol (e.g., 'BTCUSDT').
        side: The order side ('BUY' or 'SELL').
        quantity: The amount to trade.

    Returns:
        A dictionary containing the order response, or None if an error occurred.
    """
    try:
        logging.info(f"Attempting to place MARKET {side} order for {quantity} {symbol}.")
        
        # Use a spinner to show the user that the bot is working
        with console.status("[bold green]Placing market order...[/bold green]"):
            order = client.futures_create_order(
                symbol=symbol,
                side=side.upper(),
                type='MARKET',
                quantity=quantity
            )
        
        logging.info("SUCCESS: Order placed -> %s", order)
        
        # Create and print a rich table for the successful order
        table = Table(title="✅ [bold green]Market Order Placed Successfully[/bold green]", show_header=True, header_style="bold magenta")
        table.add_column("Attribute", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Order ID", str(order['orderId']))
        table.add_row("Symbol", order['symbol'])
        table.add_row("Side", order['side'])
        table.add_row("Quantity", order['origQty'])
        table.add_row("Status", f"[bold green]{order['status']}[/bold green]")
        
        console.print(table)
        return order
        
    except BinanceAPIException as e:
        logging.error(f"API ERROR placing market order: {e}")
        # Use rich to print the error in a styled box for better visibility
        console.print(f"[bold red]API ERROR:[/bold red] {e}", style="on_red")
        return None

if __name__ == "__main__":
    # Display the banner at the start of execution
    show_welcome_banner()
    
    # Argument Parsing 
    parser = argparse.ArgumentParser(description="Place a market order on Binance Futures Testnet.")
    parser.add_argument("symbol", help="The trading symbol (e.g., BTCUSDT)")
    parser.add_argument("side", choices=['BUY', 'SELL'], help="The order side (BUY or SELL)")
    parser.add_argument("quantity", type=float, help="The quantity to trade")

    args = parser.parse_args()

    #Client Initialization and Order Placement
    try:
        binance_client_wrapper = BinanceClient()
        if binance_client_wrapper.client:
            place_market_order(
                client=binance_client_wrapper.client, 
                symbol=args.symbol.upper(), 
                side=args.side.upper(), 
                quantity=args.quantity
            )
    except ValueError as e:
        console.print(f"[bold red]CONFIGURATION ERROR:[/bold red] {e}", style="on_red")
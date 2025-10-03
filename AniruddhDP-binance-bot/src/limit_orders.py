import argparse
from typing import Dict, Optional
from binance import Client
from client import BinanceClient, logging
from binance.exceptions import BinanceAPIException

from rich.console import Console
from rich.table import Table
from pyfiglet import Figlet

# Initialize the rich console for beautiful printing
console = Console()

def show_welcome_banner():
    """Displays a cool ASCII art banner for the bot."""
    banner = Figlet(font='slant')
    console.print(f"[bold cyan]{banner.renderText('Futures Bot')}[/bold cyan]")
    console.print("--- [yellow]A CLI-Based Trading Bot for Binance USDT-M Futures[/yellow] ---", justify="center")
    console.print()

def place_limit_order(client: Client, symbol: str, side: str, quantity: float, price: float) -> Optional[Dict]:
    """
    Places a limit order and displays the result in a formatted table.

    Args:
        client: An initialized Binance client instance.
        symbol: The trading symbol (e.g., 'BTCUSDT').
        side: The order side ('BUY' or 'SELL').
        quantity: The amount to trade.
        price: The price at which to place the limit order.

    Returns:
        A dictionary containing the order response, or None if an error occurred.
    """
    try:
        logging.info(f"Attempting to place LIMIT {side} order for {quantity} {symbol} at price {price}.")

        # Use a spinner to show the user that the bot is working
        with console.status("[bold green]Placing limit order...[/bold green]"):
            order = client.futures_create_order(
                symbol=symbol,
                side=side.upper(),
                type='LIMIT',
                timeInForce='GTC',  # Good 'Til Canceled
                quantity=quantity,
                price=price
            )

        logging.info("SUCCESS: Order placed -> %s", order)

        # Create and print a rich table for the successful order
        table = Table(title="✅ [bold green]Limit Order Placed Successfully[/bold green]", show_header=True, header_style="bold magenta")
        table.add_column("Attribute", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Order ID", str(order['orderId']))
        table.add_row("Symbol", order['symbol'])
        table.add_row("Side", order['side'])
        table.add_row("Price", f"[bold yellow]{order['price']}[/bold yellow]")
        table.add_row("Quantity", order['origQty'])
        table.add_row("Status", f"[bold green]{order['status']}[/bold green]")
        
        console.print(table)
        return order
        
    except BinanceAPIException as e:
        logging.error(f"API ERROR placing limit order: {e}")
        # Use rich to print the error in a styled box for better visibility
        console.print(f"[bold red]API ERROR:[/bold red] {e}", style="on_red")
        return None

if __name__ == "__main__":
    # Display the banner at the start of execution
    show_welcome_banner()
    
    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description="Place a limit order on Binance Futures Testnet.")
    parser.add_argument("symbol", help="The trading symbol (e.g., BTCUSDT)")
    parser.add_argument("side", choices=['BUY', 'SELL'], help="The order side (BUY or SELL)")
    parser.add_argument("quantity", type=float, help="The quantity to trade")
    parser.add_argument("price", type=float, help="The limit price for the order")

    args = parser.parse_args()

    # --- Client Initialization and Order Placement ---
    try:
        binance_client_wrapper = BinanceClient()
        if binance_client_wrapper.client:
            place_limit_order(
                client=binance_client_wrapper.client,
                symbol=args.symbol.upper(),
                side=args.side.upper(),
                quantity=args.quantity,
                price=args.price
            )
    except ValueError as e:
        console.print(f"[bold red]CONFIGURATION ERROR:[/bold red] {e}", style="on_red")
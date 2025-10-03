import argparse
from binance import Client
from client import BinanceClient, logging
from binance.exceptions import BinanceAPIException

# CLI Imports
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

def place_oco_orders(client: Client, symbol: str, side: str, quantity: float, take_profit_price: float, stop_loss_price: float):
    """
    Places OCO (One-Cancels-the-Other) orders and displays the results in a formatted table.

    This function places two separate 'reduceOnly' orders for an existing position:
    1. A LIMIT order for taking profit.
    2. A STOP_MARKET order for stopping loss.

    Args:
        client: An initialized Binance client instance.
        symbol: The trading symbol (e.g., 'BTCUSDT').
        side: The side of your initial position ('BUY' or 'SELL').
        quantity: The size of the position to close.
        take_profit_price: The price for the take-profit limit order.
        stop_loss_price: The trigger price for the stop-loss market order.
    """
    opposite_side = 'SELL' if side.upper() == 'BUY' else 'BUY'

    try:
        with console.status("[bold green]Placing OCO orders...[/bold green]"):
            # 1. Place the Take-Profit Limit Order
            logging.info(f"Placing Take-Profit LIMIT {opposite_side} order at price {take_profit_price}.")
            tp_order = client.futures_create_order(
                symbol=symbol, side=opposite_side, type='LIMIT', timeInForce='GTC',
                quantity=quantity, price=take_profit_price, reduceOnly=True
            )
            logging.info("SUCCESS: Take-Profit order placed -> %s", tp_order)

            # 2. Place the Stop-Loss Order
            logging.info(f"Placing Stop-Loss STOP_MARKET {opposite_side} order with stop price {stop_loss_price}.")
            sl_order = client.futures_create_order(
                symbol=symbol, side=opposite_side, type='STOP_MARKET',
                quantity=quantity, stopPrice=stop_loss_price, reduceOnly=True
            )
            logging.info("SUCCESS: Stop-Loss order placed -> %s", sl_order)

        # Create and print a rich table for the successful OCO orders
        table = Table(title="✅ [bold green]OCO Orders Placed Successfully[/bold green]", show_header=True, header_style="bold magenta")
        table.add_column("Order Type", style="cyan")
        table.add_column("Order ID", style="white")
        table.add_column("Details", style="white")

        table.add_row(
            "Take-Profit (LIMIT)",
            str(tp_order['orderId']),
            f"Side: {tp_order['side']}, Price: [bold yellow]{tp_order['price']}[/bold yellow], Status: [bold green]{tp_order['status']}[/bold green]"
        )
        table.add_row(
            "Stop-Loss (STOP_MARKET)",
            str(sl_order['orderId']),
            f"Side: {sl_order['side']}, Stop Price: [bold red]{sl_order['stopPrice']}[/bold red], Status: [bold green]{sl_order['status']}[/bold green]"
        )
        
        console.print(table)

    except BinanceAPIException as e:
        logging.error(f"API ERROR placing OCO orders: {e}")
        console.print(f"[bold red]API ERROR:[/bold red] {e}", style="on_red")

if __name__ == "__main__":
    show_welcome_banner()
    
    parser = argparse.ArgumentParser(description="Place OCO (Take-Profit and Stop-Loss) orders for an existing position.")
    parser.add_argument("symbol", help="The trading symbol (e.g., BTCUSDT)")
    parser.add_argument("side", choices=['BUY', 'SELL'], help="The side of your OPEN POSITION (e.g., BUY if you are long)")
    parser.add_argument("quantity", type=float, help="The quantity of the position to protect")
    parser.add_argument("take_profit_price", type=float, help="The take-profit trigger price")
    parser.add_argument("stop_loss_price", type=float, help="The stop-loss trigger price")

    args = parser.parse_args()

    try:
        binance_client_wrapper = BinanceClient()
        if binance_client_wrapper.client:
            place_oco_orders(
                client=binance_client_wrapper.client,
                symbol=args.symbol.upper(),
                side=args.side.upper(),
                quantity=args.quantity,
                take_profit_price=args.take_profit_price,
                stop_loss_price=args.stop_loss_price
            )
    except ValueError as e:
        console.print(f"[bold red]CONFIGURATION ERROR:[/bold red] {e}", style="on_red")
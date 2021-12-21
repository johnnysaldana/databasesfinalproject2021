import rich
import pathlib
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from rich import pretty
from rich.prompt import Prompt
from rich.prompt import Confirm
from rich.console import Console
from rich.table import Table
from stock_dao import execute_stored_procedure, get_or_write_stocks
from stock_analysis import *
from time import sleep
pretty.install()
PATH = str(pathlib.Path().resolve())
pd.options.display.max_rows = 100

# ask user whether already have account or not

def login_flow():
    console = Console()
    console.print("[white]Welcome to the[/white][bold magenta] Stock Analyzer! 💰📈[/bold magenta]")
    while (True):
        account = Prompt.ask("Do you have an account?", choices=["Y", "N"])

        # if user answers "y" prompt to login (email), if answer is "n" prompt to include new user info 
        if account == 'Y':
            in_email = Prompt.ask("Enter email: ")
            data = execute_stored_procedure("retrieveName", [in_email])
            if "error" in data[0]:
                console.print("[red]That email was not found. Please try again or register![/red]")
            else:
                console.print(f"[bold green]Login success![/bold green]\n...\n[bold magenta]Welcome {data[0]}![/bold magenta]")
                return
        elif account == 'N':
            fname = Prompt.ask("Enter first name: ")
            lname = Prompt.ask("Enter last name: ")
            new_email = Prompt.ask("Enter email (ex. firstname123@gmail.com): ")
            data = execute_stored_procedure("generateApiUser", [fname, lname, new_email])
            if not(data):
                api_key = execute_stored_procedure("retrieveApiKey", [new_email])
                console.print(f"[bold green]Created Account![/bold green]\n...\n[bold magenta]Welcome {fname}![/bold magenta]")
                console.print(f"Your api key is {api_key}")
                return
            if "error" in data[0]:
                console.print("[red]That email is already in use![/red]")

# ask user whether already have account or not

def action_screen():
    console = Console()
    while (True):
        action = Prompt.ask("""
            [bold white]Select an action to perform[/bold white]
                [bold blue](1)[/bold blue] Download stock data
                [bold blue](2)[/bold blue] Display stock data
                [bold blue](3)[/bold blue] Plot stock comparisons
                [bold blue](4)[/bold blue] SMA trend analysis
                [bold blue](5)[/bold blue] Generate correlation matrix
                [bold blue](6)[/bold blue] Generate Cointegration matrix
                [bold blue](7)[/bold blue] Trade simulator
                [bold blue](8)[/bold blue] Exit""")

        # if user answers "y" prompt to login (email), if answer is "n" prompt to include new user info 
        if action == '1':
            console = Console()
            stock = Prompt.ask("Please enter a stock")
            try:
                data = get_or_write_stocks([stock])
                k = [k for k in data.keys()][0]
                df = data[k]
                start = Prompt.ask("Please enter a selection start date (YYYY-MM-DD)")
                end = Prompt.ask("Please enter a selection end date (YYYY-MM-DD)")
                df = df[(df['Date'] > start) & (df['Date'] < end)]
                console.print("[bold green]Here is a sample of your selection.[/bold green]")
                console.print(df.head(10))
                save = Prompt.ask("[bold white]Would you like to save this to /data?.[/bold white]", choices=['Y','N'])
                path = PATH +'/data/' + k + '.csv'
                if save == 'Y':
                    df.to_csv(path)
                console.print("[bold green]Successfully saved.[/bold green]")
            except:
                console.print("[red]Invalid stock[/red]")
                
        elif action == '2':
            stock = Prompt.ask("Please enter a stock")
            try:
                data = get_or_write_stocks([stock])
                print(data)
                k = [k for k in data.keys()][0]
                df = data[k]
                i = 1
                df_length = len(df)
                while True:
                    console.print(f"[bold green]Displaying rows {i}:{i + 50} out of {df_length} rows of your selection.[/bold green]")
                    console.print(df[i:i+50])
            
                    option = Prompt.ask("[bold white]Enter N for next 50. Enter E to exit.[/bold white]", choices=['N','E'])
                    if option == 'N':
                        i+=50
                    else:
                        break
            except:
                console.print("[red]Invalid stock[/red]")
                
        elif action == '3':
            stocks = Prompt.ask("Please enter a list of stocks separated by commas ex. amzn, fb, googl")
            l = [x.strip() for x in stocks.split(',')]
            try:
                data = get_or_write_stocks(l)
                option = Prompt.ask("Select a column to plot (Hint: try Normalized Close)", choices=['High', 'Low', 'Open', 'Close', 'Volume', 'Normalized Close'])
                path = PATH + '/charts/' + '-'.join([x.strip() for x in stocks.split(',')]) + '.png'
                plot_data_list(data, option, path)
                console.print(f"[bold green]Successfully saved image to {path}.[/bold green]")

            except:
                console.print("[red]Invalid stock[/red]")
                
        elif action == '4':
            stock = Prompt.ask("Please enter a stock")
            try:
                data = get_or_write_stocks([stock])
                option = Prompt.ask("Select a column to analyze (Hint: try Normalized Close)", choices=['High', 'Low', 'Open', 'Close', 'Volume', 'Normalized Close'])
                for k in data.keys():
                    df = data[k]
                    df['SMA_3'] = df.iloc[:,1].rolling(window=3).mean()
                    df['SMA_7'] = df.iloc[:,1].rolling(window=7).mean()
                    
                    console.print(f"""
                        Ticker: {k}
                        3-Day SMA (past 10 days): {[round(x) for x in list(df['SMA_3'][-10:-1])]}
                        7-Day SMA (past 10 days): {[round(x) for x in list(df['SMA_7'][-10:-1])]}""")
                    save = Prompt.ask("Would you like to save this data?", choices=['Y', 'N'])
                    if save == 'Y':
                        path = PATH + '/data/' + stock + '_SMA.csv'
                        df = df[['Date', option, 'SMA_3', 'SMA_7']]
                        df.to_csv(path)
                        console.print(f"[bold green]Successfully saved data to {path}.[/bold green]")
            except:
                console.print("[red]Invalid stock[/red]")
                
        elif action == '5':
            try:
                stocks = Prompt.ask("Please enter a list of stocks separated by commas ex. amzn, fb, googl")
                l = [x.strip() for x in stocks.split(',')]
                data = get_or_write_stocks(l)
                option = Prompt.ask("Select a column to analyze (Hint: try Normalized Close)", choices=['High', 'Low', 'Open', 'Close', 'Volume', 'Normalized Close'])
                corr, labels = correlate_stocks(data, option)
                path = PATH + '/charts/' + '-'.join([x.strip() for x in stocks.split(',')]) + '_' + option + '_correlation.png'
                corr_matrix_heatmap(corr, labels, path)
                console.print(f"[bold green]Successfully saved image to {path}.[/bold green]")

            except:
                console.print("[red]Invalid stock[/red]")
                
        elif action == '6':
            console.print("[bold red]Note:[/bold red] This is a resource intensive task so it may take a long time to process ")
            try:
                stocks = Prompt.ask("Please enter a list of stocks separated by commas ex. amzn, fb, googl")
                l = [x.strip() for x in stocks.split(',')]
                data = get_or_write_stocks(l)
                option = Prompt.ask("Select a column to analyze (Hint: try Normalized Close)", choices=['High', 'Low', 'Open', 'Close', 'Volume', 'Normalized Close'])
                pvalue_matrix, score_matrix, labels = cointegrate_stocks(data, option)
                path = PATH + '/charts/' + '-'.join([x.strip() for x in stocks.split(',')]) + '_' + option + '_cointegration.png'
                coint_matrix_heatmap(pvalue_matrix, score_matrix, labels, option, path)
                console.print(f"[bold green]Successfully saved image to {path}.[/bold green]")

            except:
                console.print("[red]Invalid stock[/red]")
                
        elif action == '7':
            try:
                stocks = Prompt.ask("Please enter two stocks separated by commas ex. amzn, fb")
                l = [x.strip().upper() for x in stocks.split(',')]
                data = get_or_write_stocks(l)
                option = Prompt.ask("Select a column to trade on (Hint: try Normalized Close)", choices=['High', 'Low', 'Open', 'Close', 'Volume', 'Normalized Close'])
                path = PATH + '/charts/' + '-'.join([x.strip() for x in stocks.split(',')]) + '_' + option + '_traderesults.png'
                money, z = trade(data[l[0]][option], data[l[1]][option], 3, 7, path)
                console.print(f"[bold magenta]Money before {1000}, money after {money}[/bold magenta]")
                console.print(f"[bold green]Successfully saved image to {path}.[/bold green]")

            except:
                console.print("[red]Invalid stock[/red]")
                
        elif action == '8':
            console.print(f"[bold magenta]Goodbye![/bold magenta]")
            return
                
if __name__ == "__main__":
    login_flow()
    action_screen()
    
                
            
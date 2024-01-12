import requests
import entries
import argparse
from rich.console import Console
from rich.table import Table

db_path = "db"
conferences = ['sosp', 'osdi', 'asplos', 'eurosys', 'hotos']
dlbp_endpoint = "https://dblp.org/search/publ/api?q="
db = entries.dump_database(db_path)

argparser = argparse.ArgumentParser()
argparser.add_argument("-r", "--refresh", help="Refresh database", action="store_true")
args = argparser.parse_args()

console = Console()

def get_dblp_entries(conference):
    if db.is_conference_in_db(conference) and not args.refresh:
        data = db.load_conference_from_db(conference) 
    else:
        console.print("Fetching entries for " + conference + " from DBLP...", style="magenta")
        data = requests.get(dlbp_endpoint + "conf:" + conference + "&h=10000&format=json").json()
    
    console.print("Adding entries for " + conference + " to database...", style="magenta")
    db.add_to_database(data, conference)

for conference in conferences: get_dblp_entries(conference)

print()
console.print("> Enter a search query to search the database", style="green")
console.print("> Enter 'exit' to exit", style="green")
print()

while True:
    query = input("> ")
    if query == "exit":
        break
    else:
        results = db.search(query.lower())
        table = Table(title="Search results")
        table.add_column("Year", justify="left", style="magenta")
        table.add_column("Conference", justify="left", style="green")
        table.add_column("Title", justify="left", style="cyan")
        table.add_column("Link", justify="left", style="yellow")
        for result in results:
            table.add_row(str(result.year), result.venue, f"[link={result.ee}]{result.title}[/link]!", result.ee)
        console.print(table)
        print()

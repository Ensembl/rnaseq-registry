from sqlalchemy.orm import declarative_base
import argparse
from ensembl.rnaseq.registry.database_schema import create_db
Base = declarative_base()

class RnaseqRegistry:
    """Interface for the RNA-Seq Registry."""

    def __init__(self, db: str) -> None:
        self.db = db

def main():
    """Main script entry-point."""
    
    parser = argparse.ArgumentParser(
        description=("Create database tables for RNA-Seq registry"),
    )
    parser.add_argument("--dbname", type=str, required=True, 
                        help="Database name for RNA-Seq registry")
    args = parser.parse_args()
    db = args.dbname
    create_db(db)

if __name__ == "__main__":
    main()

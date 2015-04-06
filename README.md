# Swiss Tournament Database README

## Requirements
- Python 2.6 or later
- PostgresQL

## Usage

To set up the tournament database and tables:

```
> psql
=> create database tournament;
=> \c tournament
=> \i tournament.sql
```

To run the python tests:

```
> python tournament_test.py
```
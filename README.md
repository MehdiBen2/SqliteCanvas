# SpaceDB Viewer

A modern SQLite database viewer with relationship visualization capabilities.

## Features

- Open and view SQLite database files
- Browse tables and their contents
- Visual representation of database relationships
- Interactive table viewing
- Graph-based relationship visualization

## Installation

1. Make sure you have Python 3.8+ installed on your system
2. Clone this repository
3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python db_viewer.py
```

2. Click the "Open Database" button to select your SQLite database file
3. Use the tabs to switch between:
   - Tables view: Browse and view table contents
   - Relationships view: See visual representation of table relationships

## Interface

- Tables Tab: Shows the contents of your database tables
  - Click on table buttons to view their contents
  - Data is displayed in a sortable grid
- Relationships Tab: Displays a graph where:
  - Nodes represent tables
  - Edges represent foreign key relationships

## Requirements

- PyQt6
- networkx
- matplotlib

## Note

Make sure your SQLite database has proper foreign key constraints defined to see the relationships in the graph view. 
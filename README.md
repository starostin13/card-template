# card-template

A Python application that generates PDF files with multiple cards having similar design, where content is loaded from a JSON file.

## Features

- Generate professional-looking cards in PDF format
- Load card content from JSON files
- Customizable card design with title, subtitle, description, and footer
- Multiple cards per page layout
- Support for both Letter and A4 page sizes
- Clean and modern card design

## Installation

1. Clone the repository:
```bash
git clone https://github.com/starostin13/card-template.git
cd card-template
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Generate a PDF from the example JSON file:

```bash
python card_generator.py cards_data.json
```

This will create a file named `cards_output.pdf` in the current directory.

### Custom Output File

Specify a custom output filename:

```bash
python card_generator.py cards_data.json -o my_cards.pdf
```

### Different Page Size

Use A4 page size instead of the default letter size:

```bash
python card_generator.py cards_data.json --page-size A4
```

### Help

View all available options:

```bash
python card_generator.py --help
```

## JSON Format

The input JSON file should follow this structure:

```json
{
  "cards": [
    {
      "title": "Card Title",
      "subtitle": "Optional Subtitle",
      "description": "Main content of the card.\nSupports multiple lines.",
      "footer": "Optional footer text"
    }
  ]
}
```

### Field Descriptions

- **title** (required): The main heading displayed at the top of the card
- **subtitle** (optional): A secondary heading below the title
- **description** (optional): The main content area, supports multi-line text with `\n`
- **footer** (optional): Small text at the bottom of the card

## Example

An example JSON file (`cards_data.json`) is included in the repository with sample cards. You can use it as a template for creating your own cards.

## Card Design

Each card features:
- 3.5" x 2" dimensions (business card size)
- Rounded corners
- Colored header bar with white title text
- Clean layout with proper spacing
- Professional color scheme

## Requirements

- Python 3.6+
- reportlab 4.0.0+

## License

MIT License
# CSV Processor

A versatile tool for processing and cleaning CSV files with a user-friendly GUI.

## Features

- **Word Match Filtering**: Search for specific text across multiple columns with case sensitivity options
- **Duplicate Removal**: Identify and remove duplicate rows based on selected columns
- **Find and Replace**: Easily replace text or null values in specific columns
- **Interactive Preview**: View the effects of your operations in real-time
- **Export Options**: Save processed data with column selection

## Installation

### Using the Executable

Simply download the latest release and run the executable file. No installation required.

### From Source

1. Clone the repository
   ```
   git clone https://github.com/utshodeytech/csv-processor.git
   cd csv-processor
   ```

2. Install dependencies
   ```
   pip install -r requirements.txt
   ```

3. Run the application
   ```
   python main_ui.py
   ```

## Building the Executable

To create a standalone executable:

```
pyinstaller --onefile --windowed --name "CSV_Processor" main_ui.py
```

The executable will be created in the `dist` folder.

## Dependencies

- PyQt5
- Polars
- PyInstaller (for building)

## Usage

1. Click the **Browse** button to select a CSV file
2. Use the tabs to select the operation you want to perform:
   - **Word Match**: Filter rows based on text content
   - **Duplicate Remover**: Remove duplicate rows
   - **Find and Replace**: Replace text in a specific column
3. Click the corresponding action button to apply the operation
4. Use the **Download Result** button to save the processed data

## Development

The application structure consists of:
- `main_ui.py`: Contains the UI and application logic
- `main.py`: Core processing functionality
- `styles.py`: UI styling

## License

[MIT License](LICENSE)
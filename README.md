# Nightreign Relic Export

A tool for exporting relic data from Elden Ring.

## Features

- Export relic data into cvs sheet

## Installation

## Installation

1. **Clone the repository**  
    Download the project as a ZIP file or use Git:
    ```bash
    git clone https://github.com/dethland/Nightreign-Relic-Export.git
    ```

2. **Install Tesseract-OCR**  
    Follow this guide to install Tesseract-OCR on Windows:  
    [Tesseract-OCR Installation Guide](https://docs.coro.net/featured/agent/install-tesseract-windows/)

3. **Install Python dependencies**  
    Run the following command in the project directory to install required modules:
    ```bash
    python install.py
    ```

## Usage

1. Open a terminal and navigate to the project directory:
    ```bash
    cd Nightreign-Relic-Export/scripts
    ```

2. Start the program:
    ```bash
    python main.py
    ```

3. Launch Elden Ring and enter the relic selection screen.

4. Press `Ctrl + Shift + F12` to begin the export process.

5. Wait for image processing to complete.

6. Find your exported relic data in the `export_data` folder.

## Configuration

- Edit `config.yaml` to customize export settings.

## Contributing

Contributions are welcome! Please open issues or submit pull requests.

## License

This project is licensed under the MIT License.

## Credits

- Inspired by Elden Ring community tools
- Developed by [Your Name]
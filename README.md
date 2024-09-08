# Rocket Parts Extractor

This Flask application processes PDF documents containing rocket or spacecraft specifications, extracts information about parts, and stores them in a SQLite database. It uses natural language processing to analyze the documents and provide searchable part information.

## Features

- PDF upload and processing
- Extraction of rocket/spacecraft parts information using LangChain and Claude AI
- Storage of parts information in a SQLite database
- Search functionality for parts information
- Web interface for uploading documents and viewing results

## Requirements

- Python 3.7+
- Flask
- LangChain
- Anthropic API key
- Other dependencies listed in `requirements.txt`

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/your-username/rocket-parts-extractor.git
   cd rocket-parts-extractor
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your Anthropic API key:
   - Create a `.env` file in the project root
   - Add your API key: `ANTHROPIC_API_KEY=your_api_key_here`

4. Run the application:
   ```
   python app.py
   ```

5. Open a web browser and navigate to `http://localhost:5000`

## Usage

1. Upload a PDF document containing rocket or spacecraft specifications.
2. The application will process the document and extract parts information.
3. View the extracted parts and their descriptions on the results page.
4. Use the search functionality to find specific parts.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Environment Setup

This project uses environment variables to securely store sensitive information. Follow these steps to set up your environment:

1. Create a `.env.local` file in the root directory of the project.
2. Add your Anthropic API key to the `.env.local` file:
   ```
   ANTHROPIC_API_KEY=your_actual_api_key_here
   ```
3. Replace `your_actual_api_key_here` with your real Anthropic API key.

Note: The `.env.local` file is ignored by Git to keep your API key secure. Never commit this file or share it publicly.
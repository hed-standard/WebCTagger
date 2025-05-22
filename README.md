# CTagger Web app
Web form for CTagger and also include a automated tag suggestion experimental feature using calls to OpenAI.

## Technical Stack

### Backend
- **Framework**: Flask (Python 3.11)
- **Key Dependencies**:
  - Flask-CORS for cross-origin resource sharing
  - OpenAI API integration for automated tag suggestions
  - HED Tools for HED tag processing
  - Python-dotenv for environment variable management including OpenAI key

### Frontend
- **UI Framework**: Bootstrap 5.3.3
- **JavaScript Libraries**:
  - jQuery for DOM manipulation and AJAX
  - JSON View for JSON visualization
  - D3.js for data visualization
  - DataTables for table management
  - jQuery UI for autocomplete functionality

### Infrastructure
- **Containerization**: Docker
- **Deployment**: AWS Elastic Beanstalk

### Key Features
1. **File Processing**:
   - Support for BIDS-style events.json/tsv files
   - JSON visualization with collapsible tree view
   - TSV to JSON conversion

2. **HED Tag Management**:
   - Interactive schema browser
   - Tag search and autocomplete
   - Tag suggestion using OpenAI integration
   - Support for standard and library schemas

3. **User Interface**:
   - Responsive design with Bootstrap
   - Interactive JSON viewer
   - Dynamic form population
   - Real-time tag suggestions

### Project Structure and Main Files

#### Backend Files
- **`board/__init__.py`**: Flask application initialization
  - Sets up the Flask app with CORS support
  - Registers blueprints for routing

- **`board/pages.py`**: Main application logic
  - Handles HTTP routes and request processing
  - Manages file uploads and JSON/TSV processing
  - Implements HED tag generation and validation

- **`board/openai_api.py`**: OpenAI integration
  - Manages communication with OpenAI API
  - Handles tag suggestion generation
  - Includes model training capabilities

- **`board/create_hed_prompts.py`**: HED prompt generation
  - Creates structured prompts for OpenAI
  - Manages HED tag formatting and validation

#### Frontend Files
- **`board/templates/pages/home.html`**: Main application interface
  - Implements the user interface
  - Handles file upload forms
  - Manages JSON visualization
  - Integrates schema browser

- **`board/static/js/schema-browser.js`**: Schema management
  - Handles HED schema loading and navigation
  - Implements tag search and autocomplete
  - Manages schema version selection

- **`board/static/js/custom.js`**: Custom functionality
  - Implements file processing logic
  - Manages form interactions
  - Handles JSON/TSV conversion

#### Configuration Files
- **`Dockerfile`**: Container configuration
  - Sets up Python environment
  - Installs dependencies
  - Configures application port

- **`requirements.txt`**: Python dependencies
  - Lists all required Python packages
  - Specifies version requirements

- **`.env`**: Environment configuration
  - Stores OpenAI API key
  - Manages environment variables

### Installation
- Clone the repo
- Create `.env` file and specify a single line
`OPENAI_API_KEY=xxxxxx`
- Run `docker build -t ctagger .` in the top-level directory
- Run `docker run -p 8080:5000 ctagger`
- The app can be accessed with `https://localhost:8080`
**Warning: if it works this might incur a large charge to the OpenAI account**

Author: Dung "Young" Truong - May 2025
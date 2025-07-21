PDF RAG: Chat with Your Documents
=================================

This project provides a powerful and simple-to-use backend service that allows you to "chat" with your PDF documents. By leveraging a Retrieval-Augmented Generation (RAG) architecture, you can upload a PDF and ask questions about its content, enabling you to quickly find information and summarize key details.

Features
--------

*   **PDF Upload**: Securely upload PDF files via a simple API endpoint.
    
*   **Document Processing**: Automatically extracts text, splits it into manageable chunks, and creates vector embeddings.
    
*   **Information Retrieval**: Ask questions in natural language and receive concise, relevant answers sourced directly from the document.
    
*   **Vector Search**: Uses Pinecone's high-performance vector database to find the most relevant document chunks for any query.
    
*   **Easy to Deploy**: Built with FastAPI, making the server lightweight and easy to run.
    

Technology Stack
----------------

This project is built with a modern Python stack designed for building AI-powered applications:

*   **Backend Framework**: [**FastAPI**](https://fastapi.tiangolo.com/) for building a high-performance REST API.
    
*   **Frontend Framework**: [**Streamlit**](https://streamlit.io/) for creating an interactive web interface.
    
*   **LLM Orchestration**: [**LangChain**](https://www.langchain.com/) to structure the interactions between the language model, data, and APIs.
    
*   **Vector Database**: [**Pinecone**](https://www.pinecone.io/) for efficient storage and retrieval of vector embeddings.
    
*   **Embedding Model**: [**Sentence-Transformers**](https://www.sbert.net/) (all-MiniLM-L6-v2) for converting text chunks into meaningful vector representations.
    
*   **Language Model (LLM)**: Easily configurable to work with models from providers like **Nebius AI**, **OpenAI**, and others.
    

Getting Started
---------------

Follow these instructions to get the project running on your local machine.

### Prerequisites

*   Python 3.8+
    
*   Git
    
*   A Pinecone account (free tier is available)
    
*   An API key from an LLM provider (e.g., Nebius AI)
    

### Installation

1.  git clone https://github.com/your-username/PDF\_RAG.git
    
2.  cd PDF\_RAG
    
3.  \# For Windows
    
4.  python -m venv venv.\\venv\\Scripts\\activate#
    
5.  For macOS/Linux
    
6.  python3 -m venv venvsource venv/bin/activate
    
7.  pip install -r requirements.txt
    

### Configuration

1.  Create a .env file in the root directory of the project. This file will hold your secret keys.
    
2.  \# Pinecone CredentialsPINECONE\_API\_KEY="YOUR\_PINECONE\_API\_KEY"PINECONE\_ENVIRONMENT="YOUR\_PINECONE\_ENVIRONMENT" # e.g., "gcp-starter"# LLM Provider API KeyNEBIUS\_API\_KEY="YOUR\_NEBIUS\_API\_KEY"
    

Usage
-----

### Running the Application

To run the full application, you need to start both the backend server and the frontend interface in two separate terminals.

**1\. Start the Backend (FastAPI)**

In your first terminal, run the following command from the project's root directory:

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   uvicorn main:app --reload   `

The backend API will be available at http://127.0.0.1:8000.

**2\. Start the Frontend (Streamlit)**

In a second terminal, run this command from the project's root directory:

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   streamlit run Frontend/frontend.py   `

The Streamlit web interface will open in your browser, typically at http://localhost:8501.

### API Endpoints

The backend provides the following APIs, which are used by the frontend:

*   **POST /upload**
    
    *   **Description**: Uploads a PDF file for processing.
        
    *   **Body**: multipart/form-data with a file attached.
        
    *   **Response**: A confirmation message indicating the number of chunks stored.
        
*   **GET /retrieve**
    
    *   **Description**: Asks a question about the uploaded document(s).
        
    *   **Query Parameter**: query (string).
        
    *   **Example**: http://127.0.0.1:8000/retrieve?query=What+is+the+main+topic+of+the+document
        
    *   **Response**: A JSON object containing the LLM's answer.
        
*   **POST /clear-database**
    
    *   **Description**: Deletes all vectors from the Pinecone index. **Use with caution!**
        
    *   **Response**: A success message.

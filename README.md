# Project: AI & Image Color Detection Server

## Overview

This project is a **Node.js** server application that provides two main functionalities:

1. **Interact with OpenAI's GPT Model**: The server can receive prompts from the user, send them to the OpenAI API, and return the generated response from the GPT model.
2. **Color Detection via Image Upload**: Users can upload three images, which will be passed to a Python script for color detection or other image processing. The results are then returned as JSON, and the uploaded files are deleted after processing to clean up server space.

The server is built using **Express** and is capable of handling image uploads with **Multer** and interacting with the OpenAI API using **Axios**. It also integrates a Python script for image processing.

## Features

- **OpenAI Integration**: Interacts with OpenAI's GPT-4 model to generate responses based on user prompts.
- **Image Upload & Processing**: Allows users to upload three images, which are then processed by a Python script. The server returns color detection results.
- **Environment Configuration**: Configurable via environment variables for security and flexibility.
- **Error Handling**: Comprehensive error handling for both OpenAI API interactions and image processing.
- **Temporary File Handling**: Automatically deletes uploaded image files after processing to free up server space.

## Table of Contents

- [Installation](#installation)
- [Setup](#setup)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
  - [POST /api/openai](#post-apiopenai)
  - [POST /api/detect-colors](#post-apidetect-colors)
- [Python Script for Color Detection](#python-script-for-color-detection)
- [Running the Server](#running-the-server)
- [Error Handling](#error-handling)
- [File Structure](#file-structure)
- [License](#license)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/idan-nave/ai-image-recognition-server.git
   cd ai-image-detection-server
   ```

2. **Install dependencies**:
   Use **npm** to install the required Node.js packages:
   ```bash
   npm install
   ```

3. **Install Python Dependencies**:
   The project requires Python for color detection. Ensure that you have Python installed and then install any required Python packages (if needed):
   ```bash
   pip install -r scripts/requirements.txt
   ```

## Setup

1. **Set up the environment**:
   Create a `.env` file in the root directory of your project and add the necessary configuration.

   Example `.env` file:
   ```
   OPENAI_API_KEY=your-openai-api-key
   ```

2. **Python Script Setup**:
   Ensure that the Python script `scripts/rubiks_cube_color_detector.py` exists and is properly set up to handle the color detection or other image processing tasks.

## Environment Variables

The application relies on the following environment variables:

- **OPENAI_API_KEY**: Your API key for OpenAI's GPT service.

To set up the `.env` file:
- Create a `.env` file in the root directory.
- Add your OpenAI API key as follows:
  ```
  OPENAI_API_KEY=your-openai-api-key
  ```

## API Endpoints

### POST /api/openai

**Purpose**: Interact with OpenAI's GPT model by sending a prompt and receiving a response.

**Request Body**:
```json
{
  "prompt": "Your prompt here",
  "max_tokens": 100
}
```

- `prompt`: The input text you want to send to the GPT model.
- `max_tokens`: (Optional) The maximum number of tokens for the response (default: 100).

**Response**:
A JSON response containing the model’s output.

**Example Request**:
```bash
curl -X POST http://localhost:3000/api/openai -H "Content-Type: application/json" -d '{"prompt": "Tell me a joke", "max_tokens": 50}'
```

### POST /api/detect-colors

**Purpose**: Upload three images to detect their colors using a Python script.

**Request**:
- Three image files must be uploaded as form-data. The keys must be `image1`, `image2`, and `image3`.

**Form Data**:
- `image1`: The first image file.
- `image2`: The second image file.
- `image3`: The third image file.

**Response**:
A JSON response containing the color detection results, or an error if the process fails.

**Example Request**:
```bash
curl -X POST http://localhost:3000/api/detect-colors -F "image1=@path/to/image1.jpg" -F "image2=@path/to/image2.jpg" -F "image3=@path/to/image3.jpg"
```

## Python Script for Color Detection

The Python script `scripts/check.py` is used to process the uploaded images. It should be designed to accept three image file paths, analyze the images, and return the results in a JSON format.

### Example Python Script Output:
```json
{
  "image1": { "dominantColor": "#FF5733", "otherColors": ["#FF6347", "#FFD700"] },
  "image2": { "dominantColor": "#4CAF50", "otherColors": ["#8BC34A", "#C8E6C9"] },
  "image3": { "dominantColor": "#3F51B5", "otherColors": ["#2196F3", "#BBDEFB"] }
}
```

## Running the Server

1. **Start the server**:
   After setting up your environment, start the server with the following command:
   ```bash
   node server.js
   ```

2. **Access the API**:
   The server will run on `http://localhost:3000`. You can now make requests to the API endpoints.

## Dependecies

    "axios": "^1.7.8",          // For making HTTP requests (like OpenAI API calls)
    "cors": "^2.8.5",           // To enable CORS
    "dotenv": "^16.4.5",        // For loading environment variables from a .env file
    "express": "^4.21.1",       // Web framework for the Node.js server
    "multer": "^1.4.5-lts.1",   // For handling multipart/form-data, used for file uploads
    "child_process": "^1.0.2",  // Allows you to spawn child processes (e.g., to run the Python script)
    "path": "^0.12.7",          // Node.js utility for working with file and directory paths
    "fs": "0.0.1",              // Node.js file system module for reading and writing files
    "python-shell": "^3.0.0"    // (Optional) If you'd like to use this for executing Python scripts from Node.js

## Deploying on Render

To deploy the server-ai-image-recognition app on Render, you need to configure the Build Command and Start Command correctly.

    Build Command: Render runs this command to install the Python dependencies from your requirements.txt file before each deployment. This ensures that all necessary Python libraries (like numpy, pillow, etc.) are installed and available for the backend Python processing.

   $ npm run install-python-deps

   Start Command: Render runs this command to start your Node.js server after the build process is complete. It launches the main Express server defined in server.js to handle incoming requests.

    $ node server.js

Make sure that your requirements.txt file is located in the scripts/ folder and contains all the necessary Python dependencies for the image recognition logic. Render will automatically handle the installation and execution of both Python and Node.js components, allowing your app to function seamlessly.


## Error Handling

- If the OpenAI API key is missing or incorrect, the server will return a `500` error with the message `Missing OpenAI API Key`.
- If a prompt is missing from the request body, the server will return a `400` error with the message `Missing prompt in request body`.
- For the `/api/detect-colors` endpoint, if fewer than three images are uploaded, the server will return a `400` error with the message `Please upload 3 images.`
- If the Python script fails or returns invalid JSON, the server will return a `500` error with the message `Invalid JSON from Python script.`
- Any unexpected errors will be caught and logged, with an appropriate error message returned to the client.

## File Structure

```
/
├── server.js            # Main server file
├── .env                 # Environment variables (API keys)
├── package.json         # Node.js dependencies and scripts
├── scripts/             # Python scripts for image processing
│   └── check.py         # Python script for color detection (or other image tasks)
└── uploads/             # Temporary storage for uploaded files
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

This project provides an easy-to-use backend server that combines OpenAI's powerful GPT model and Python image processing in one application. You can use it to interact with the OpenAI API for natural language tasks and analyze images for color detection or other purposes.
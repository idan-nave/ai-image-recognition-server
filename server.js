// Import required packages
const express = require('express');
const axios = require('axios');
const cors = require('cors');
const multer = require('multer');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
require('dotenv').config();

// Initialize the Express app and configure the port
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware configuration
app.use(cors()); // Enable Cross-Origin Resource Sharing (CORS)
app.use(express.json()); // Middleware to parse JSON bodies

// Set up Multer for handling image uploads
const upload = multer({ dest: 'uploads/' }); // Images are stored temporarily in 'uploads' folder

// API endpoint to interact with OpenAI (Chat GPT model)
app.post('/api/openai', async (req, res) => {
  console.log('Request received:', req.body);

  // Extract prompt and max_tokens from request body
  const { prompt, max_tokens } = req.body;
  const OPENAI_API_KEY = process.env.OPENAI_API_KEY; // Read API key from environment variables

  // Validate API key and prompt
  if (!OPENAI_API_KEY) {
    console.error('Missing OpenAI API Key');
    return res.status(500).json({ error: 'Missing OpenAI API Key' });
  }

  if (!prompt) {
    console.error('Missing prompt in request body');
    return res.status(400).json({ error: 'Missing prompt in request body' });
  }

  try {
    // Make a request to OpenAI API
    const response = await axios.post(
      'https://api.openai.com/v1/chat/completions',
      {
        model: 'gpt-4', // Specify the model to use (GPT-4)
        messages: [
          { role: 'system', content: 'You are a helpful assistant.' },
          { role: 'user', content: prompt },
        ],
        max_tokens: max_tokens || 100, // Set max tokens or default to 100
      },
      {
        headers: {
          Authorization: `Bearer ${OPENAI_API_KEY}`, // Pass the API key in Authorization header
        },
      }
    );

    console.log('OpenAI Response:', response.data);
    res.json(response.data); // Send OpenAI response as JSON to client
  } catch (error) {
    console.error('Error communicating with OpenAI:', error.message);
    // Error handling for OpenAI API request
    if (error.response) {
      console.error('Error response data:', error.response.data);
      res.status(error.response.status).json(error.response.data);
    } else {
      res.status(500).json({ error: error.message });
    }
  }
});

// API endpoint to detect colors from uploaded images using a Python script
app.post('/api/detect-colors', upload.fields([{ name: 'image1' }, { name: 'image2' }, { name: 'image3' }]), (req, res) => {
  const { files } = req;
  console.log('Uploaded files:', files);

  // Check if the necessary images were uploaded
  if (!files.image1 || !files.image2 || !files.image3) {
    return res.status(400).json({ error: 'Please upload 3 images.' });
  }

  // Get paths of uploaded images
  const imagePaths = [files.image1[0].path, files.image2[0].path, files.image3[0].path];
  console.log('Image paths:', imagePaths);

  // Spawn Python process to run color detection script
  const python = spawn('python3', ['scripts/rubiks_cube_color_detector.py', ...imagePaths]);

  let pythonOutput = '';
  python.stdout.on('data', (data) => {
    console.log('Python output:', data.toString());
    pythonOutput += data.toString(); // Collect Python script output
  });

  python.stderr.on('data', (data) => {
    console.error('Python error:', data.toString());
  });

  python.on('close', (code) => {
    console.log('Python script exited with code:', code);

    // Clean up uploaded files after processing
    imagePaths.forEach((filePath) => {
      console.log('Deleting file:', filePath);
      fs.unlinkSync(filePath); // Remove image files from server
    });

    if (code === 0) {
      try {
        const result = JSON.parse(pythonOutput); // Parse the output from Python script (assuming it is JSON)
        res.json(result); // Return parsed result to client
      } catch (error) {
        console.error('JSON parse error:', error);
        res.status(500).json({ error: 'Invalid JSON from Python script.' });
      }
    } else {
      res.status(500).json({ error: 'Python script failed.' });
    }
  });
});

// Start the server on the specified port
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
import random
import os

app = FastAPI()

# Define expert data with names and skills
expert_data = [
    {'name': 'Dr. Anjali Mehta', 'skills': 'AI, ML, Data Science'},
    {'name': 'Prof. Raghav Sharma', 'skills': 'AI, Robotics, Automation'},
    {'name': 'Dr. Priya Nair', 'skills': 'ML, Deep Learning, Neural Networks'},
    {'name': 'Dr. Sanjay Verma', 'skills': 'Data Science, AI, NLP'},
    {'name': 'Dr. Neha Kulkarni', 'skills': 'AI, ML, Computer Vision'},
    {'name': 'Dr. Amit Kumar', 'skills': 'Data Science, Deep Learning'},
    {'name': 'Dr. Shreya Agarwal', 'skills': 'ML, Neural Networks'},
    {'name': 'Dr. Mohan Rao', 'skills': 'Automation, Robotics'},
    {'name': 'Dr. Swati Patel', 'skills': 'AI, Computer Vision'},
    {'name': 'Dr. Varun Desai', 'skills': 'AI, ML'}
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.get("/")
async def get_html():
    # Serve the HTML file
    return FileResponse(os.path.join(BASE_DIR, "post1.html"))

@app.get("/api/experts")
async def get_experts():
    # Generate random relevance scores for each expert and return their data
    experts_data = [
        {"name": expert['name'], "skills": expert['skills'], "relevance": random.randint(50, 100)}
        for expert in expert_data
    ]
    return JSONResponse(content=experts_data)

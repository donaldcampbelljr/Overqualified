import os
import json
import time
import requests
from flask import Flask, jsonify
from flask_cors import CORS

# --- Configuration ---
# NOTE: The API key is assumed to be available as an environment variable
# in the Docker container for security.
API_KEY = os.environ.get('GEMINI_API_KEY', "") # Use environment variable for production/deployment
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"

# Cached fictional resumes for fallback when API key is not available
CACHED_RESUMES = [
    {
        "name": "Dr. Whiskers McFluffington",
        "title": "Chief Happiness Officer & Professional Cat Herder",
        "summary": "Seasoned feline management specialist with over 12 years of experience in optimizing purr productivity and implementing state-of-the-art nap scheduling systems. Expert in cross-species communication and emergency yarn detangling.",
        "contact": {
            "email": "whiskers.mcfluff@purrfectcorp.com",
            "phone": "(555) MEOW-CAT",
            "location": "Catnip Valley, CA"
        },
        "experience": [
            {
                "company": "Purrfect Corporation",
                "role": "Senior Nap Coordinator",
                "duration": "2019 - Present",
                "description": "Revolutionized workplace productivity by implementing mandatory 14-hour nap schedules, resulting in 300% increase in employee satisfaction and purr frequency."
            },
            {
                "company": "Fuzzy Logic Solutions",
                "role": "Lead Treat Distribution Analyst",
                "duration": "2015 - 2019",
                "description": "Developed proprietary algorithms for optimal treat distribution timing, reducing workplace hissing incidents by 87% and increasing tail wag metrics."
            },
            {
                "company": "Yarn Ball Enterprises",
                "role": "Junior String Theory Specialist",
                "duration": "2012 - 2015",
                "description": "Conducted extensive research in advanced string entanglement patterns and their applications in modern cat entertainment systems."
            }
        ],
        "skills": [
            "Advanced Purring Techniques",
            "Professional Box Sitting",
            "Laser Dot Tracking",
            "Tuna Can Opening",
            "Strategic Hairball Placement"
        ]
    },
    {
        "name": "Captain Nebula Stardust",
        "title": "Intergalactic Pizza Delivery Specialist",
        "summary": "Experienced cosmic courier with expertise in delivering hot, fresh pizza across multiple galaxies within 30 minutes or less. Fluent in 47 alien languages and certified in zero-gravity cheese stretching techniques.",
        "contact": {
            "email": "nebula.stardust@cosmicpizza.galaxy",
            "phone": "(555) UFO-PIZZA",
            "location": "Space Station Alpha-7, Milky Way"
        },
        "experience": [
            {
                "company": "Cosmic Pizza Co.",
                "role": "Senior Wormhole Navigator",
                "duration": "2020 - Present",
                "description": "Successfully delivered over 10,000 pizzas across 12 solar systems with a 99.7% on-time delivery rate, even during black hole traffic jams."
            },
            {
                "company": "Martian Munchies Inc.",
                "role": "Asteroid Belt Route Manager",
                "duration": "2017 - 2020",
                "description": "Pioneered the first commercial delivery routes through the asteroid belt, reducing delivery times to outer planets by 40% while maintaining pizza temperature integrity."
            },
            {
                "company": "Saturn Ring Restaurants",
                "role": "Anti-Gravity Training Instructor",
                "duration": "2014 - 2017",
                "description": "Trained over 200 delivery pilots in zero-gravity pizza handling techniques and emergency comet evasion maneuvers."
            }
        ],
        "skills": [
            "Hyperdrive Navigation",
            "Alien Customer Service",
            "Zero-G Pizza Spinning",
            "Meteorite Dodging",
            "Universal Translator Proficiency"
        ]
    },
    {
        "name": "Professor Bubble Maximillian",
        "title": "Chief Bubble Engineer & Sudsy Solutions Architect",
        "summary": "Distinguished bubble scientist with a PhD in Advanced Soap Dynamics and over 15 years of experience in creating the perfect bubble solutions. Holds 23 patents in bubble longevity technology and rainbow reflection optimization.",
        "contact": {
            "email": "bubble.max@soapscience.com",
            "phone": "(555) POP-SOAP",
            "location": "Bubble Bay, Rainbow Islands"
        },
        "experience": [
            {
                "company": "Rainbow Bubble Dynamics",
                "role": "Principal Soap Scientist",
                "duration": "2018 - Present",
                "description": "Led breakthrough research in self-repairing bubble membranes, achieving record-breaking bubble lifespans of up to 3.7 hours in controlled environments."
            },
            {
                "company": "Sudsy Solutions Laboratory",
                "role": "Senior Foam Architect",
                "duration": "2013 - 2018",
                "description": "Designed revolutionary bubble-blowing apparatus capable of producing bubbles in 47 different geometric shapes, including dodecahedrons and Klein bottles."
            },
            {
                "company": "Giggle & Pop Entertainment",
                "role": "Bubble Show Coordinator",
                "duration": "2009 - 2013",
                "description": "Orchestrated over 500 bubble performances for audiences ranging from birthday parties to intergalactic peace summits, achieving 100% giggle satisfaction rates."
            }
        ],
        "skills": [
            "Molecular Soap Engineering",
            "Advanced Bubble Choreography",
            "Wind Resistance Calculations",
            "Rainbow Refraction Analysis",
            "Professional Giggle Induction"
        ]
    }
]

app = Flask(__name__)
# Enable CORS for the React frontend running on a different port/container
CORS(app)

# Define the JSON schema for the resume structure
RESUME_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "name": {"type": "STRING", "description": "Full name of the fictional professional."},
        "title": {"type": "STRING", "description": "Their unique job title or profession (e.g., Chief Fun Officer)."},
        "summary": {"type": "STRING", "description": "A brief, one-paragraph professional summary."},
        "contact": {
            "type": "OBJECT",
            "properties": {
                "email": {"type": "STRING"},
                "phone": {"type": "STRING"},
                "location": {"type": "STRING"}
            }
        },
        "experience": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "company": {"type": "STRING", "description": "Fictional company name."},
                    "role": {"type": "STRING", "description": "Job role at the company."},
                    "duration": {"type": "STRING", "description": "Start and end dates (e.g., '2020 - Present')."},
                    "description": {"type": "STRING", "description": "Key achievement or responsibility in one sentence."}
                },
                "required": ["company", "role", "duration", "description"]
            },
            "description": "A list of 2 to 3 relevant work experiences."
        },
        "skills": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
            "description": "A list of 5 key, sometimes absurd, skills."
        }
    },
    "required": ["name", "title", "summary", "contact", "experience", "skills"]
}

def generate_resume_from_gemini():
    """Calls the Gemini API to generate a structured JSON resume."""
    
    # System instruction guiding the model's persona and output
    system_prompt = (
        "You are an AI specializing in writing highly engaging and structured professional resumes "
        "for fictional characters with extremely creative or quirky professions. "
        "The output MUST strictly adhere to the provided JSON schema."
    )
    
    # User prompt asking for the content
    user_query = "Generate a complete, structured resume for a fictional character. Give them a highly unusual or quirky job title and experience."
    
    payload = {
        "contents": [{ "parts": [{ "text": user_query }] }],
        "systemInstruction": {
            "parts": [{ "text": system_prompt }]
        },
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": RESUME_SCHEMA
        }
    }
    
    headers = { 'Content-Type': 'application/json' }
    
    # Exponential backoff for API robustness
    max_retries = 3
    delay = 2
    
    for attempt in range(max_retries):
        try:
            # Append the API key to the URL
            full_api_url = f"{API_URL}?key={API_KEY}"
            
            print(f"Making API request attempt {attempt + 1}/{max_retries}")
            
            # Use 'requests' to make the API call
            response = requests.post(full_api_url, headers=headers, data=json.dumps(payload), timeout=60)  # Increased timeout
            
            print(f"API response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"API error response: {response.text}")
                response.raise_for_status()
            
            result = response.json()
            print("API response received successfully")

            # Check for content and parse the structured JSON string
            if (result.get('candidates') and 
                len(result['candidates']) > 0 and
                result['candidates'][0].get('content') and 
                result['candidates'][0]['content'].get('parts') and
                len(result['candidates'][0]['content']['parts']) > 0):
                
                json_string = result['candidates'][0]['content']['parts'][0]['text']
                print(f"Received JSON response: {json_string[:100]}...")
                
                # The response is a JSON string, so we must parse it
                resume_data = json.loads(json_string)
                print("Successfully parsed JSON response")
                return resume_data, 200
            else:
                print(f"API returned unexpected structure: {result}")
                return {"error": "API returned no valid content structure."}, 500

        except requests.exceptions.Timeout:
            print(f"Attempt {attempt + 1} timed out")
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2
            else:
                return {"error": "API request timed out after multiple retries."}, 500
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed with network error: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2
            else:
                return {"error": f"Failed to connect to the LLM API after multiple retries: {str(e)}"}, 500
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return {"error": "LLM response could not be parsed as valid JSON."}, 500
        except Exception as e:
            print(f"Unexpected error: {e}")
            return {"error": f"An unexpected error occurred: {e}"}, 500
    
    return {"error": "Max retries exceeded"}, 500


@app.route('/api/resume', methods=['GET'])
def get_resume():
    """Endpoint to trigger the dynamic resume generation or serve cached resume."""
    print("=" * 50)
    print("Request received for resume...")
    
    # Check if API Key is set
    if not API_KEY:
        print("API key not found, serving cached resume...")
        import random
        cached_resume = random.choice(CACHED_RESUMES)
        return jsonify(cached_resume)

    print(f"API key present: {len(API_KEY)} characters")
    
    # Try to generate from API, fall back to cached if it fails
    try:
        resume_data, status_code = generate_resume_from_gemini()
        
        if status_code != 200:
            print(f"API generation failed with status {status_code}, serving cached resume...")
            print(f"Error details: {resume_data}")
            import random
            cached_resume = random.choice(CACHED_RESUMES)
            return jsonify(cached_resume)
        
        print("Successfully generated and serving AI resume data.")
        return jsonify(resume_data)
    except ValueError as e:
        # This catches the case where generate_resume_from_gemini doesn't return a tuple
        print(f"Unexpected return format from API function: {e}. Serving cached resume...")
        import random
        cached_resume = random.choice(CACHED_RESUMES)
        return jsonify(cached_resume)
    except Exception as e:
        print(f"Unexpected error generating resume from API: {e}. Serving cached resume...")
        import random
        cached_resume = random.choice(CACHED_RESUMES)
        return jsonify(cached_resume)

if __name__ == '__main__':
    # Running directly (for testing outside Docker)
    app.run(debug=True, host='0.0.0.0', port=5000)

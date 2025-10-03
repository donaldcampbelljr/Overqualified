import React, { useState, useEffect, useCallback } from 'react';

// Use a simple, minimal App setup since we assume a basic CRA/Vite environment
// which handles the main index.html setup.

// Helper component for section headers
const SectionHeader = ({ title }) => (
  <h2 className="text-xl font-bold text-gray-700 border-b-2 border-indigo-500 pb-1 mb-4 uppercase tracking-wider mt-6">
    {title}
  </h2>
);

// Fallback structure for type checking and initial state
const defaultResume = {
  name: "Generating Fictional Professional...",
  title: "Waiting for LLM Data",
  summary: "Please ensure your Gemini API key is set in docker-compose.yml and the backend service is running correctly.",
  contact: { email: "loading@example.com", phone: "555-555-5555", location: "Global Network" },
  experience: [],
  skills: []
};

// Main App Component
const App = () => {
  const [resume, setResume] = useState(defaultResume);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // NOTE: Use relative URL since we're proxying through the same domain
  // When running with Docker Compose, the proxy in package.json will handle this
  const API_URL = '/api/resume';

  const fetchResume = useCallback(async () => {
    setLoading(true);
    setError(null);

    // Simple exponential backoff retry loop (client-side)
    const maxRetries = 3;
    let delay = 1000;

    for (let i = 0; i < maxRetries; i++) {
        try {
            const response = await fetch(API_URL);
            
            if (!response.ok) {
                // If response is not ok (e.g., 404, 500), try to read error message from body
                const errorData = await response.json().catch(() => ({ error: 'Server returned a non-JSON error.' }));
                throw new Error(errorData.error || `HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            setResume(data);
            setLoading(false);
            return; // Success, exit function
        } catch (err) {
            console.error(`Fetch attempt ${i + 1} failed:`, err.message);
            if (i < maxRetries - 1) {
                // Wait before retrying
                await new Promise(resolve => setTimeout(resolve, delay));
                delay *= 2;
            } else {
                // Final failure
                setError(`Failed to fetch resume after ${maxRetries} attempts: ${err.message}`);
                setLoading(false);
            }
        }
    }
  }, []);

  useEffect(() => {
    fetchResume();
  }, [fetchResume]);

  const renderContent = () => {
    if (loading) {
      return (
        <div className="flex justify-center items-center h-48">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          <p className="ml-4 text-gray-600">Generating a new fictional persona...</p>
        </div>
      );
    }

    if (error) {
      return (
        <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
          <p className="font-bold">Error Loading Resume</p>
          <p className="text-sm">{error}</p>
          <p className="text-xs mt-2">Check the Python backend logs (port 5000) and ensure the GEMINI_API_KEY is correct in your `docker-compose.yml`.</p>
        </div>
      );
    }

    // --- Resume Rendering ---
    return (
      <div className="space-y-6">
        {/* Contact Info */}
        <div className="flex flex-col sm:flex-row justify-between text-sm text-gray-600 pb-2 border-b">
          <span>📧 {resume.contact.email}</span>
          <span>📞 {resume.contact.phone}</span>
          <span>📍 {resume.contact.location}</span>
        </div>

        {/* Summary */}
        <div className="bg-gray-50 p-4 rounded-lg shadow-inner">
          <SectionHeader title="Professional Summary" />
          <p className="text-gray-700 leading-relaxed text-sm italic">
            {resume.summary}
          </p>
        </div>

        {/* Experience */}
        <div>
          <SectionHeader title="Experience" />
          {resume.experience && resume.experience.map((job, index) => (
            <div key={index} className="mb-4 p-4 border-l-4 border-indigo-400 pl-4 transition duration-300 hover:bg-indigo-50 rounded-md">
              <h3 className="text-lg font-semibold text-gray-800">{job.role}</h3>
              <p className="text-indigo-600 font-medium">{job.company}</p>
              <p className="text-xs text-gray-500 mb-2">{job.duration}</p>
              <ul className="list-disc ml-5 text-gray-600 text-sm">
                <li>{job.description}</li>
              </ul>
            </div>
          ))}
        </div>

        {/* Skills */}
        <div>
          <SectionHeader title="Skills & Proficiencies" />
          <div className="flex flex-wrap gap-2">
            {resume.skills && resume.skills.map((skill, index) => (
              <span 
                key={index} 
                className="bg-indigo-100 text-indigo-800 text-xs font-semibold px-3 py-1 rounded-full shadow-sm hover:bg-indigo-200 transition duration-150"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      </div>
    );
  };

  return (
    // Main container with Tailwind setup
    <div className="min-h-screen bg-gray-100 font-sans p-4 sm:p-8 flex justify-center">
      <div className="w-full max-w-4xl bg-white shadow-2xl rounded-xl p-6 sm:p-10 border border-gray-200">
        
        {/* Header */}
        <header className="mb-8 text-center">
          <h1 className="text-4xl sm:text-5xl font-extrabold text-gray-900 tracking-tighter leading-none">
            {resume.name}
          </h1>
          <p className="text-xl text-indigo-600 mt-1 font-light italic">
            {resume.title}
          </p>
        </header>

        {/* Main Content & Button */}
        <div className="mb-6">
          <button
            onClick={fetchResume}
            disabled={loading}
            className={`w-full py-3 rounded-lg text-white font-bold text-lg shadow-lg transition duration-300 transform 
            ${loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700 hover:scale-[1.01] active:scale-[0.99]'}
            `}
          >
            {loading ? 'Generating...' : 'Generate New Fictional Resume'}
          </button>
        </div>

        {renderContent()}

        {/* Footer */}
        <footer className="mt-10 pt-4 border-t text-center text-xs text-gray-400">
            Powered by React, Python (Flask), and the Gemini API for dynamic content generation.
        </footer>
      </div>
    </div>
  );
};

export default App;
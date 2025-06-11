import React, { useState } from "react";

export default function PoemEditor() {
  const [lines, setLines] = useState([""]);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Handle textarea change
  const handleChange = (e) => {
    const value = e.target.value;
    setLines(value.split("\n").slice(0, 3)); // Only keep up to 3 lines
  };

  // Call backend for suggestions
  const suggestNextLine = async () => {
    setLoading(true);
    setError("");
    setSuggestions([]);
    try {
      const res = await fetch("http://localhost:8000/suggest-line", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lines }),
      });
      if (!res.ok) throw new Error("Failed to fetch suggestions");
      const data = await res.json();
      setSuggestions(data.suggestions || []);
    } catch (err) {
      setError("Could not get suggestions. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  // Accept a suggestion
  const acceptSuggestion = (suggestion) => {
    setLines([...lines, suggestion].slice(-3)); // Keep last 3 lines
    setSuggestions([]);
  };

  return (
    <div className="max-w-xl mx-auto mt-16 bg-white shadow-lg rounded-lg p-8">
      <h1 className="text-2xl font-bold mb-4 text-center">Virelya – Your Poetry Muse</h1>
      <textarea
        className="w-full h-32 p-3 border border-gray-300 rounded mb-4 focus:outline-none focus:ring"
        value={lines.join("\n")}
        onChange={handleChange}
        placeholder="Write 1–3 lines of your poem..."
        maxLength={240}
      />
      <button
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        onClick={suggestNextLine}
        disabled={loading || lines.filter(Boolean).length === 0}
      >
        {loading ? "Thinking..." : "Suggest Next Line"}
      </button>
      {error && <div className="text-red-600 mt-2">{error}</div>}
      {suggestions.length > 0 && (
        <div className="mt-6">
          <div className="font-semibold mb-2">AI Suggestions:</div>
          <ul>
            {suggestions.map((s, i) => (
              <li key={i} className="mb-2 flex items-center">
                <span className="flex-1 italic">{s}</span>
                <button
                  className="ml-4 bg-green-500 text-white px-3 py-1 rounded hover:bg-green-600"
                  onClick={() => acceptSuggestion(s)}
                >
                  Accept
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

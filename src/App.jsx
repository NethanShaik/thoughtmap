import { useState } from 'react'
import './App.css'

function App() {
  const [inputText, setInputText] = useState("");
  const [result, setResult] = useState(null);

  const analyzeText = () => {
    setResult({
      main: "This text discusses AI explainability.",
      intent: "The author wants to educate readers",
      controversy: "Raises concerns about AI transparency."
    });
  }

  return (
      <div style={{padding:"40px"}}>
        <h1>ThoughtMap AI</h1>
        <textarea
          rows="6"
          style={{width:"100%"}}
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          />
        <br /><br />
        <button onClick={analyzeText}>
          Analyze
        </button>
      {result &&(
        <div>
          <h3>Main Idea</h3>
          <p>{result.main}</p>

          <h3>Author Intent</h3>
          <p>{result.intent}</p>

          <h3>Potential Controversy</h3>
          <p>{result.controversy}</p>
        </div>
      )}
      </div>
  );
}

export default App

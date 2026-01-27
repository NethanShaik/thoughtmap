import { useState } from 'react'
import ConceptGraph from './components/ConceptGraph';

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
    <div className="w-full min-h-screen bg-gradient-to-br from-[#55B6EF] to-[#F6F6DD]">
      <div className="w-full max-w-5xl mx-auto px-6 py-10 flex flex-col items-center gap-6 text-center">
        <h1 className ="text-4xl font-bold"> ThoughtMap AI </h1>
        <p className='text-grey-300 font-bold'>
          Paste text and we'll visualize how the model understands it.
        </p>
        <textarea
        className="w-full p-4 rounded-lg bg-white/30 border border-gray-700 backdrop-blur-md focus:outline-none focus:ring-2 focus:ring-blue-400"
          rows="6"
          placeholder='Paste your text here...'
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          />
        <br /><br />
        <button onClick={analyzeText}
        className="glass-button">
         <span className='relative z-10'>Analyze </span>
         <span
              className="
                          absolute inset-0
                          rounded-2xl
                          bg-gradient-to-br from-white/70 to-transparent
                          opacity-30
                          pointer-events-none
                        "
          />
        </button>
      {result &&(
        <div className="grid gap-4 pt-4">
          <div className="glass-result">
            <h3 className="font-semibold text-black-300 mb-1">Main Idea</h3>
            <p className="text-black-300">{result.main}</p>
          </div>

          <div className="glass-result">
            <h3 className="font-semibold text-black-300 mb-1">Author Intent</h3>
            <p className='text-grey-300'>{result.intent}</p>
          </div>

          <div className="glass-result">
            <h3 className="font-semibold text-black-300 mb-1">Potential Controversy</h3>
            <p className='text-grey-300'>{result.controversy}</p>
        </div>
        <div className="w-full max-w-4xl pt-6 text-left">
        <h2 className="text-2xl font-semibold text-black-300 mb-3">
          Thought Map
        </h2>
        <ConceptGraph />
     </div>
      </div>
      )}
      </div>
    </div>
  );
}

export default App

import { useState } from 'react'

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
    <div className="min-h-screen w-[100vw] bg-gradient-to-b from-blue-900 via-blue-950 to-black text-white">



      <div className="w-full max-w-5xl mx-auto px-6 py-10 flex flex-col items-center gap-6 text-center">
        <h1 className='text-4xl font-bold text-green-400'> ThoughtMap AI </h1>
        <p className='text-grey-300'>
          Paste text and we'll visualize how the model understands it.
        </p>
        <textarea
        className="w-full p-4 rounded-lg bg-gray-800 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-green-400"
          rows="6"
          placeholder='Paste your text here...'
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          />
        <br /><br />
        <button onClick={analyzeText}
        className="px-6 py-2 bg-green-500 text-black font-semibold rounded-lg hover:bg-green-400 transition">
          Analyze
        </button>
      {result &&(
        <div className="grid gap-4 pt-4">
          <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
            <h3 className="font-semibold text-green-300 mb-1">Main Idea</h3>
            <p className="text-gray-300">{result.main}</p>
          </div>

          <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
            <h3 className="font-semibold text-green-300 mb-1">Author Intent</h3>
            <p className='text-grey-300'>{result.intent}</p>
          </div>

          <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
            <h3 className="font-semibold text-green-300 mb-1">Potential Controversy</h3>
            <p className='text-grey-300'>{result.controversy}</p>
        </div>
      </div>
      )}
      </div>
    </div>
  );
}

export default App

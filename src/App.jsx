import ConceptGraph from './components/ConceptGraph';
import {useRef, useState} from "react";

function App() {
  const graphRef = useRef(null);
  const [inputText, setInputText] = useState("");
  const [result, setResult] = useState(null);
  const [threshold, setThreshold] = useState(0.2);
  const [graph, setGraph] = useState({nodes: [], edges: []});

  const resetAll = () =>{
    window.scrollTo({top:0, behavior:"smooth"});
    setTimeout(() => {
    setInputText("");
    setResult(null);
    setGraph({nodes:[], edges:[]});
    }, 100);
  };

  const analyzeText = async() => {
    if (!inputText.trim()) return;
    try{
      const res = await fetch("http://127.0.0.1:8000/analyze",{
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({
          text: inputText,
          edge_threshold: Number(threshold),
        }),
      });

      const data = await res.json();
      if(!res.ok || data.error){
        console.error(data);
        alert(data.error || "Analyze Failed");
        return;
      }

      const mappedNodes = data.nodes.map((n, i) => ({
        id: n.id,
        data: { label: n.label },
        position: { x: 80 + (i % 2) * 420, y: 60 + Math.floor(i / 2) * 160 },
      }));

      const mappedEdges = data.edges.map((e,i)=>({
        id: `e-${i}`,
        source: e.source,
        target: e.target,
        label: String(e.weight),
      }));

      setGraph({nodes: mappedNodes, edges: mappedEdges});
      

      setResult({
        main: data.cards.mainIdea,
        intent: data.cards.authorIntent,
        controversy: data.cards.controversy,
      });

      setTimeout(() => {
        graphRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      },0);
    } catch(err) {
      console.error(err);
      alert("Backend not reachable (check FastAPI is running on :8000)");
    }
  };

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

      <div className="w-full max-w-xl text-left">
          <label className="font-semibold">
            Edge threshold: <span className="font-mono">{Number(threshold).toFixed(2)}</span>
          </label>
          <input
            type="range"
            min="0.10"
            max="0.40"
            step="0.01"
            value={threshold}
            onChange={(e) => setThreshold(e.target.value)}
            className="w-full"
          />
          <p className="text-sm text-gray-600">
            Lower = more connections, Higher = stricter.
          </p>
        </div>

        <br /><br />
       {!result ? (
         <button onClick={analyzeText}
        className="glass-button">
         <span className='relative z-10'>Analyze </span>
         <span className="absolute inset-0 rounded-2xl bg-gradient-to-br from-white/70 to-transparent opacity-30 pointer-events-none"/>
        </button>
       ):(
        <button onClick={resetAll}
          className="glass-button">
            <span className='relative z-10'>Reset </span>
            <span className="absolute inset-0 rounded-2xl bg-gradient-to-br from-white/70 to-transparent opacity-30 pointer-events-none"/>
          </button>
       )}
      {result &&(
        <>
        <div className="grid gap-4 pt-4 w-full max-w-4xl">
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
        </div>
        <div ref={graphRef} className="w-full max-w-4xl pt-6 text-left">
        <h2 className="text-2xl font-semibold text-black-300 mb-3">
          Thought Map
        </h2>
        <ConceptGraph nodes={graph.nodes} edges={graph.edges}/>
     </div>
      </>
      )}
      </div>
    </div>
  );
}

export default App

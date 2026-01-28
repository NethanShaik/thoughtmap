import ConceptGraph from './components/ConceptGraph';
import {useRef, useState} from "react";

function App() {
  const graphRef = useRef(null);
  const [inputText, setInputText] = useState("");
  const [result, setResult] = useState(null);
  const [graph, setGraph] = useState({nodes: [], edges: []});
  const STOP = new Set([
    "the","and","a","to","of","in","is","it","that","for","on","with","as","are",
    "this","be","by","an","or","from","at","was","were","has","have","had","but",
   "should","more","most","strictly","proper","without","however","may","might","can","could",
   "would","will","also","into","over","under","than","then","there","their","these","those",
   "them","your","about","because","while","which","when","where","what","why","how"
  ])

  function topConcepts(text, k = 8){
    const words = text
    .toLowerCase()
    .replace(/[^a-z\s]/g," ")
    .split(/\s+/)
    .filter(Boolean)
    .filter(w => w.length >= 4 && !STOP.has(w));

    const freq = new Map();
    for (const w of words) freq.set(w, (freq.get(w) || 0) + 1);

    return [...freq.entries()]
    .sort((a,b) => b[1] - a[1])
    .slice(0,k)
    .map(([w]) => w);
  }

  function buildGraph(concepts){
    const nodes = concepts.map((c,i) => ({
      id:String(i+1),
      data: {label:c},
      position: {x:60 + (i%4)*180, y: 60 + Math.floor(i/4) * 160},
    }));
    
    const edges = concepts.slice(1).map((_,i) => ({
      id: `e1-${i+2}`,
      source:"1",
      target: String(i+2)
    }));
    return {nodes,edges};

  }

  function summarizeHeuristic(text,concepts){
    const firstSentence = text.trim().split(/[.!?]\s/)[0] || "No text provided.";
    const main = concepts.length
    ? `Main:theme: ${concepts[0]} (and related: ${concepts.slice(1,4).join(", ") || "-"}).`
    : "Main theme: (not enough text).";

    const intent = 
    text.includes("?") ? "Likely asking a question / seeking clarification."
    : text.toLowerCase().includes("should") || text.toLowerCase().includes("must")
      ?"Likely giving advice or making a recommendation."
      :"Likely explaining or describing something.";

    const controversyWords = ["bias", "risk", "concern", "problem", "controversy", "harm", "ethics", "privacy", "transparency"];
    const hits = controversyWords.filter(w => text.toLowerCase().includes(w));
    const controversy = hits.length
    ? `Mentions potential concerns: ${hits.join(", ")}.`
    : "No obvious controversy keywords detected.";

    return {main: `${main} (Starts with: "${firstSentence}...")`, intent, controversy};
  }

  const resetAll = () =>{
    window.scrollTo({top:0, behavior:"smooth"});
    setTimeout(() => {
    setInputText("");
    setResult(null);
    setGraph({nodes:[], edges:[]});
    }, 100);
  };

  const analyzeText = () => {
    if (!inputText.trim()) return;
    const concepts = topConcepts(inputText, 8);
    const graphData = buildGraph(concepts);
    const analysis = summarizeHeuristic(inputText, concepts);
    setGraph(graphData);
    setResult(analysis);

    setTimeout(() => {
      graphRef.current?.scrollIntoView({behavior:"smooth",block:"start"});
    }, 0);
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

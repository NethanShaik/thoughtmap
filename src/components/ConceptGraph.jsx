import ReactFlow from "reactflow";
import "reactflow/dist/style.css";

const nodes = [
    {id: "1", position: {x:250, y:50}, data: {label: "Main Idea"}},
    {id: "2", position: {x:100, y:160}, data: {label: "Intent"}},
    {id: "3", position: {x:400, y:160}, data: {label: "Controversy"}},
];

const edges = [
    {id: "e1-2", source: "1", target: "2"},
    {id: "e1-3", source: "1", target: "3"},
];

export default function ConceptGraph(){
    return (
        <div className="w-full max-w-4xl h-[450px] rounded-lg border border-gray-700 bg-gray-900/40">
            <ReactFlow nodes = {nodes} edges = {edges} fitView />
        </div>
    );
}
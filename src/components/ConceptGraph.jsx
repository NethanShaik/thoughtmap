import ReactFlow, { ReactFlowProvider } from "reactflow";
import "reactflow/dist/style.css";

export default function ConceptGraph({ nodes = [], edges = [] }) {
  return (
    <div className="w-full max-w-4xl">
      {/* IMPORTANT: this wrapper MUST have an explicit height */}
      <div style={{ width: "100%", height: 450 }}>
        <ReactFlowProvider>
          <ReactFlow nodes={nodes} edges={edges} fitView />
        </ReactFlowProvider>
      </div>
    </div>
  );
}

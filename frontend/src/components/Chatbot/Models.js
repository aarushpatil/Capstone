import React from "react";

const MODEL_OPTIONS = [
  { value: "tinyllama", label: "TinyLlama" },
  { value: "mistral",    label: "Mistral 7B" },
  { value: "wizardlm",   label: "WizardLM 13B" },
];

const Models = ({ selected, onChange }) => (
  <div className="mb-4 px-6">
    <label className="block text-sm font-medium text-gray-700 mb-1">
      Choose Model
    </label>
    <select
      value={selected}
      onChange={e => onChange(e.target.value)}
      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
    >
      {MODEL_OPTIONS.map(m => (
        <option key={m.value} value={m.value}>
          {m.label}
        </option>
      ))}
    </select>
  </div>
);

export default Models;

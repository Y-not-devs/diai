import React from 'react';
import { DiagnosisResult } from '../../types';

interface DiagnosisCardProps {
  result: DiagnosisResult;
  rank: number;
}

export const DiagnosisCard: React.FC<DiagnosisCardProps> = ({ result, rank }) => {
  let borderColor = 'border-gray-500';
  let badgeColor = 'bg-gray-500/20 text-gray-300';
  let confidenceText = 'Низкая вероятность';

  if (result.confidence >= 0.8) {
    borderColor = 'border-red-500';
    badgeColor = 'bg-red-500/20 text-red-400';
    confidenceText = 'Высокая вероятность';
  } else if (result.confidence >= 0.5) {
    borderColor = 'border-yellow-500';
    badgeColor = 'bg-yellow-500/20 text-yellow-400';
    confidenceText = 'Средняя вероятность';
  }

  return (
    <div className={`glass-panel p-6 border-l-4 ${borderColor} transition-all hover:bg-white/10`}>
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-xl font-bold text-white flex items-center gap-3">
            <span className="text-gray-500 text-lg">#{rank}</span>
            {result.diagnosis}
          </h3>
          <span className="inline-block bg-white/10 text-gray-300 text-xs px-2 py-1 rounded mt-2 font-mono border border-white/5">
            МКБ-10: {result.icd_10}
          </span>
        </div>
        <div className="flex flex-col items-end">
          <span className={`${badgeColor} text-sm font-semibold px-3 py-1 rounded-full border border-white/5`}>
            {confidenceText}
          </span>
          <span className="text-xs text-gray-400 mt-2 font-mono">
            {(result.confidence * 100).toFixed(1)}% Совпадение
          </span>
        </div>
      </div>
      <div className="mt-4 pt-4 border-t border-white/10">
        <p className="text-gray-300 text-sm leading-relaxed">
          <strong className="text-white font-medium">Обоснование:</strong> {result.explanation}
        </p>
        <p className="text-gray-500 text-xs mt-3 flex items-center gap-1">
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
          Источник: {result.protocol_title}
        </p>
      </div>
    </div>
  );
};

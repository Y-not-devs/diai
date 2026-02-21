import React from 'react';
import { DiagnosisResult } from '../../types';
import { DiagnosisCard } from './DiagnosisCard';

interface DiagnosisListProps {
  results: DiagnosisResult[];
  isLoading: boolean;
}

export const DiagnosisList: React.FC<DiagnosisListProps> = ({ results, isLoading }) => {
  if (isLoading) {
    return (
      <div className="space-y-4 w-full">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
          <h2 className="text-lg font-medium text-gray-300">Анализ симптомов по клиническим протоколам...</h2>
        </div>
        {[1, 2, 3].map((i) => (
          <div key={i} className="glass-panel p-6 border-l-4 border-white/10 animate-pulse">
            <div className="h-6 bg-white/10 rounded w-1/3 mb-3"></div>
            <div className="h-4 bg-white/5 rounded w-1/4 mb-6"></div>
            <div className="h-4 bg-white/5 rounded w-full mb-2"></div>
            <div className="h-4 bg-white/5 rounded w-5/6"></div>
          </div>
        ))}
      </div>
    );
  }

  if (results.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4 w-full">
      <div className="flex justify-between items-center mb-6 px-2">
        <h2 className="text-lg font-medium text-white">Топ-{results.length} возможных диагнозов</h2>
        <span className="text-sm text-gray-400">Отсортировано по вероятности</span>
      </div>
      <div className="grid gap-4">
        {results.map((result, index) => (
          <DiagnosisCard key={result.id} result={result} rank={index + 1} />
        ))}
      </div>
    </div>
  );
};

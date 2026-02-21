import React from 'react';
import { Message } from '../../types';
import { DiagnosisList } from '../diagnosis/DiagnosisList';

interface ChatMessageProps {
  message: Message;
  onRetry?: () => void;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message, onRetry }) => {
  const isUser = message.role === 'user';
  const isError = message.type === 'error';

  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} mb-6`}>
      <div className={`max-w-[85%] flex gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
          isUser ? 'bg-white/20' : isError ? 'bg-red-500/20 border border-red-500/30' : 'bg-white/5 border border-white/10'
        }`}>
          {isUser ? (
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
          ) : isError ? (
            <svg className="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
          ) : (
            <div className="w-3 h-3 bg-white rounded-full"></div>
          )}
        </div>

        {/* Content */}
        <div className={`flex flex-col gap-3 ${isUser ? 'items-end' : 'items-start'}`}>
          <div className={`px-5 py-3 rounded-2xl text-[15px] leading-relaxed ${
            isUser 
              ? 'bg-white/10 text-white rounded-tr-sm' 
              : isError
                ? 'bg-red-500/10 text-red-200 border border-red-500/20'
                : 'bg-transparent text-gray-200'
          }`}>
            {message.content}
            
            {isError && onRetry && (
              <button 
                onClick={onRetry}
                className="mt-3 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-300 rounded-lg text-sm font-medium transition flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                Перезагрузить чат
              </button>
            )}
          </div>
          
          {message.type === 'diagnosis' && message.diagnoses && (
            <div className="w-full mt-2">
              <DiagnosisList results={message.diagnoses} isLoading={false} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

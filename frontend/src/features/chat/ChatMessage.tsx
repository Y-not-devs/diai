import React from 'react';
import { Message } from '../../types';
import { DiagnosisList } from '../diagnosis/DiagnosisList';

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} mb-6`}>
      <div className={`max-w-[85%] flex gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${isUser ? 'bg-white/20' : 'bg-white/5 border border-white/10'}`}>
          {isUser ? (
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
          ) : (
            <div className="w-3 h-3 bg-white rounded-full"></div>
          )}
        </div>

        {/* Content */}
        <div className={`flex flex-col gap-3 ${isUser ? 'items-end' : 'items-start'}`}>
          <div className={`px-5 py-3 rounded-2xl text-[15px] leading-relaxed ${
            isUser 
              ? 'bg-white/10 text-white rounded-tr-sm' 
              : 'bg-transparent text-gray-200'
          }`}>
            {message.content}
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

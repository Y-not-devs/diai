import { useState, useRef, useEffect } from 'react';
import { ChatInput } from './features/chat/ChatInput';
import { ChatMessage } from './features/chat/ChatMessage';
import { sendMessageToAI } from './api/diagnosis';
import { Message } from './types';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = async (text: string) => {
    const newUserMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      type: 'text',
      content: text,
    };

    const updatedMessages = [...messages, newUserMsg];
    setMessages(updatedMessages);
    setIsLoading(true);

    try {
      const aiResponse = await sendMessageToAI(updatedMessages);
      setMessages([...updatedMessages, aiResponse]);
    } catch (error) {
      console.error('Error sending message:', error);
      // TODO: Add error handling UI
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-screen flex flex-col relative overflow-hidden bg-[#050505]">
      {/* Header */}
      <header className="w-full p-4 flex justify-between items-center z-30 border-b border-white/5 bg-[#050505]/80 backdrop-blur-md absolute top-0">
        <div className="flex items-center gap-3">
          <button 
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
          </button>
        </div>
        <div className="font-bold text-lg tracking-tight flex items-center gap-2 text-white absolute left-1/2 -translate-x-1/2">
          <div className="w-5 h-5 bg-white rounded-full"></div>
          Qazcode CDSS
        </div>
        <div className="w-9"></div> {/* Spacer for centering */}
      </header>

      {/* Floating Sidebar */}
      <div className={`fixed top-20 left-4 bottom-28 w-72 glass-panel z-20 transition-all duration-300 ease-in-out transform ${isSidebarOpen ? 'translate-x-0 opacity-100' : '-translate-x-[120%] opacity-0 pointer-events-none'}`}>
        <div className="p-4 h-full flex flex-col">
          <h3 className="text-white font-medium mb-4 px-2">История чатов</h3>
          <div className="flex-1 overflow-y-auto space-y-2">
            {/* Mock history items */}
            <button className="w-full text-left px-3 py-2 rounded-lg hover:bg-white/10 text-gray-300 text-sm transition truncate">
              Пациент с головной болью
            </button>
            <button className="w-full text-left px-3 py-2 rounded-lg hover:bg-white/10 text-gray-300 text-sm transition truncate">
              Подозрение на пневмонию
            </button>
            <button className="w-full text-left px-3 py-2 rounded-lg hover:bg-white/10 text-gray-300 text-sm transition truncate">
              Анализ крови: отклонения
            </button>
          </div>
          <button className="mt-4 w-full py-2 rounded-lg border border-white/10 text-white text-sm hover:bg-white/10 transition flex items-center justify-center gap-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path></svg>
            Новый чат
          </button>
        </div>
      </div>

      {/* Chat Area */}
      <main className="flex-1 overflow-y-auto pt-20 pb-32 px-4 w-full flex flex-col items-center scroll-smooth">
        {messages.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center max-w-2xl mx-auto animate-in fade-in duration-700">
            <h1 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight text-white">
              Медицинский ИИ-ассистент
            </h1>
            <p className="text-gray-400 text-lg">
              Опишите симптомы пациента, и я помогу определить диагноз на основе официальных клинических протоколов РК.
            </p>
          </div>
        ) : (
          <div className="w-full max-w-3xl flex flex-col gap-2">
            {messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))}
            
            {isLoading && (
              <div className="flex w-full justify-start mb-6">
                <div className="max-w-[85%] flex gap-4 flex-row">
                  <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 bg-white/5 border border-white/10">
                    <div className="w-3 h-3 bg-white rounded-full"></div>
                  </div>
                  <div className="flex items-center gap-2 px-5 py-4 rounded-2xl bg-transparent">
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </main>

      {/* Input Area */}
      <div className="absolute bottom-0 left-0 w-full bg-gradient-to-t from-[#050505] via-[#050505]/80 to-transparent pt-10 pb-6 px-4 z-20">
        <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
        <p className="text-center text-gray-600 text-xs mt-3">
          ИИ может ошибаться. Всегда сверяйте диагнозы с официальными клиническими протоколами.
        </p>
      </div>
    </div>
  );
}

export default App;

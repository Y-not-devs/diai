import { useState, useRef, useEffect, type UIEvent } from 'react';
import { ChatInput } from './features/chat/ChatInput';
import { ChatMessage } from './features/chat/ChatMessage';
import { getChatMessages, getChats, sendMessageToBackend } from './api/diagnosis';
import { ChatMessageApi, ChatSummary, Message } from './types';

const PAGE_SIZE = 10;

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isChatsLoading, setIsChatsLoading] = useState(false);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [isHistoryLoading, setIsHistoryLoading] = useState(false);
  const [hasMoreHistory, setHasMoreHistory] = useState(false);
  const [minMessageId, setMinMessageId] = useState<number | undefined>(undefined);
  const [chats, setChats] = useState<ChatSummary[]>([]);
  const [selectedChatId, setSelectedChatId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatScrollRef = useRef<HTMLDivElement>(null);

  // Временные ID для тестов
  const [userId] = useState('user-' + Math.random().toString(36).substring(7));
  const [chatId, setChatId] = useState('chat-' + Date.now().toString());

  const mapApiMessage = (msg: ChatMessageApi): Message => {
    const isDiagnosis = msg.answer_type === 0 && Array.isArray(msg.diagnosis);
    return {
      id: String(msg.message_id),
      messageId: msg.message_id,
      role: msg.role,
      type: isDiagnosis ? 'diagnosis' : 'text',
      content: msg.text,
      diagnoses: isDiagnosis ? msg.diagnosis || undefined : undefined,
      createdAt: msg.created_at,
    };
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (!isHistoryLoading) {
      scrollToBottom();
    }
  }, [messages, isLoading, isHistoryLoading]);

  useEffect(() => {
    if (!isSidebarOpen) {
      return;
    }

    const loadChats = async () => {
      setIsChatsLoading(true);
      try {
        const data = await getChats(userId);
        setChats(data.chats || []);
      } catch (error) {
        console.error('Error loading chats:', error);
      } finally {
        setIsChatsLoading(false);
      }
    };

    loadChats();
  }, [isSidebarOpen, userId]);

  useEffect(() => {
    if (!selectedChatId) {
      return;
    }

    const loadChat = async () => {
      setIsChatLoading(true);
      setMessages([]);
      setHasMoreHistory(false);
      setMinMessageId(undefined);
      try {
        const data = await getChatMessages(selectedChatId, PAGE_SIZE);
        const ordered = [...data.messages].sort((a, b) => a.message_id - b.message_id);
        setMessages(ordered.map(mapApiMessage));
        const minId = data.min_message_id ?? ordered[0]?.message_id;
        setMinMessageId(minId);
        setHasMoreHistory(Boolean(data.has_more));
      } catch (error) {
        console.error('Error loading chat:', error);
      } finally {
        setIsChatLoading(false);
      }
    };

    loadChat();
  }, [selectedChatId]);

  const handleSendMessage = async (text: string) => {
    const activeChatId = selectedChatId ?? chatId;
    const newUserMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      type: 'text',
      content: text,
    };

    setMessages((prev) => [...prev, newUserMsg]);
    setIsLoading(true);

    try {
      const response = await sendMessageToBackend({
        user_id: userId,
        chat_id: activeChatId,
        text: text,
      });

      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        type: response.answer_type === 0 ? 'diagnosis' : 'text',
        content: response.text,
        diagnoses: response.answer_type === 0 ? response.diagnosis : undefined,
      };

      setMessages((prev) => [...prev, aiMsg]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          role: 'assistant',
          type: 'error',
          content: 'Не удалось подключиться к серверу. Пожалуйста, проверьте, запущен ли бэкенд.',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetChat = () => {
    setMessages([]);
    setIsLoading(false);
    setHasMoreHistory(false);
    setMinMessageId(undefined);
    setSelectedChatId(null);
    setChatId('chat-' + Date.now().toString());
  };

  const handleSelectChat = (chat: ChatSummary) => {
    setSelectedChatId(chat.chat_id);
    setIsSidebarOpen(false);
  };

  const handleChatScroll = (event: UIEvent<HTMLDivElement>) => {
    const target = event.currentTarget;
    if (target.scrollTop < 80) {
      handleLoadMore();
    }
  };

  const handleLoadMore = async () => {
    if (!selectedChatId || !hasMoreHistory || isHistoryLoading || !minMessageId) {
      return;
    }

    const container = chatScrollRef.current;
    const prevScrollHeight = container?.scrollHeight ?? 0;
    const prevScrollTop = container?.scrollTop ?? 0;

    setIsHistoryLoading(true);
    try {
      const data = await getChatMessages(selectedChatId, PAGE_SIZE, minMessageId);
      const ordered = [...data.messages].sort((a, b) => a.message_id - b.message_id);
      setMessages((prev) => [...ordered.map(mapApiMessage), ...prev]);
      const nextMinId = data.min_message_id ?? ordered[0]?.message_id;
      setMinMessageId(nextMinId ?? minMessageId);
      setHasMoreHistory(Boolean(data.has_more));
    } catch (error) {
      console.error('Error loading more messages:', error);
    } finally {
      setIsHistoryLoading(false);
      requestAnimationFrame(() => {
        if (container) {
          const newScrollHeight = container.scrollHeight;
          container.scrollTop = newScrollHeight - prevScrollHeight + prevScrollTop;
        }
      });
    }
  };

  return (
    <div className="h-[100dvh] flex flex-col overflow-hidden bg-[#050505]">
      {/* Header */}
      <header className="shrink-0 w-full p-4 flex justify-between items-center z-30 border-b border-white/5 bg-[#050505]/80 backdrop-blur-md">
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

      {/* Sidebar overlay (mobile) */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 md:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Floating Sidebar */}
      <div className={`fixed w-72 glass-panel z-30 transition-all duration-300 ease-in-out transform top-0 left-0 h-full md:top-20 md:left-4 md:h-auto md:bottom-4 lg:rounded-2xl rounded-none ${isSidebarOpen ? 'translate-x-0 opacity-100' : '-translate-x-full opacity-0 pointer-events-none'}`}>
        <div className="p-4 h-full flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-white font-medium">История чатов</h3>
            <button
              onClick={() => setIsSidebarOpen(false)}
              className="p-1 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
          </div>
          <div className="flex-1 overflow-y-auto space-y-2">
            {isChatsLoading ? (
              <div className="text-sm text-gray-400 px-3 py-2">Загрузка чатов...</div>
            ) : chats.length === 0 ? (
              <div className="text-sm text-gray-500 px-3 py-2">Чатов пока нет</div>
            ) : (
              chats.map((chat) => (
                <button
                  key={chat.chat_id}
                  onClick={() => handleSelectChat(chat)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm transition truncate ${
                    selectedChatId === chat.chat_id
                      ? 'bg-white/10 text-white'
                      : 'text-gray-300 hover:bg-white/10'
                  }`}
                >
                  {chat.chat_name}
                </button>
              ))
            )}
          </div>
          <button 
            onClick={handleResetChat}
            className="mt-4 w-full py-2 rounded-lg border border-white/10 text-white text-sm hover:bg-white/10 transition flex items-center justify-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path></svg>
            Новый чат
          </button>
        </div>
      </div>

      {/* Chat Area */}
      <main
        ref={chatScrollRef}
        onScroll={handleChatScroll}
        className="flex-1 overflow-y-auto px-4 py-4 w-full flex flex-col items-center scroll-smooth"
      >
        {isChatLoading ? (
          <div className="flex-1 flex items-center justify-center text-gray-400">
            Загрузка истории чата...
          </div>
        ) : messages.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center max-w-2xl mx-auto py-8 animate-in fade-in duration-700">
            <h1 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight text-white">
              Медицинский ИИ-ассистент
            </h1>
            <p className="text-gray-400 text-lg px-4">
              Опишите симптомы пациента, и я помогу определить диагноз на основе официальных клинических протоколов РК.
            </p>
          </div>
        ) : (
          <div className="w-full max-w-3xl flex flex-col gap-2">
            {isHistoryLoading && (
              <div className="text-sm text-gray-400 px-3 py-2">Загрузка предыдущих сообщений...</div>
            )}
            {messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} onRetry={handleResetChat} />
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
      <div className="shrink-0 w-full bg-[#050505] p-4 border-t border-white/5">
        <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
        <p className="text-center text-gray-600 text-xs mt-3">
          ИИ может ошибаться. Всегда сверяйте диагнозы с официальными клиническими протоколами.
        </p>
      </div>
    </div>
  );
}

export default App;

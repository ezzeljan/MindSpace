import React, { useState, useRef, useEffect } from 'react';
import ChatBubble from '../components/ChatBubble';
import MessageInput from '../components/MessageInput';

const ChatPage = () => {
    const [messages, setMessages] = useState([
        {
            id: 1,
            text: "Hello. I'm MindSpace, your reflection assistant. How are you feeling today?",
            isUser: false,
        }
    ]);

    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSendMessage = (text) => {
        // Add user message
        const newUserMsg = { id: Date.now(), text, isUser: true };
        setMessages((prev) => [...prev, newUserMsg]);

        // Simulate assistant reply
        setTimeout(() => {
            const assistantReply = {
                id: Date.now() + 1,
                text: "Thank you for sharing that. Would you like to explore that feeling further?",
                isUser: false,
            };
            setMessages((prev) => [...prev, assistantReply]);
        }, 700);
    };

    return (
        <div className="h-full flex flex-col max-w-4xl mx-auto">
            <div className="mb-6 px-2">
                <h2 className="text-2xl font-semibold text-wellness-text dark:text-gray-100">Reflection Chat</h2>
                <p className="text-gray-500 dark:text-gray-400 mt-1">A safe space to share your thoughts.</p>
            </div>

            <div className="card flex-1 flex flex-col p-0 overflow-hidden bg-white/80 dark:bg-gray-800/80 transition-colors duration-300 backdrop-blur-sm">
                <div className="flex-1 overflow-y-auto p-6 flex flex-col">
                    {messages.map((msg) => (
                        <ChatBubble key={msg.id} message={msg.text} isUser={msg.isUser} />
                    ))}
                    <div ref={messagesEndRef} />
                </div>

                <MessageInput onSendMessage={handleSendMessage} />
            </div>
        </div>
    );
};

export default ChatPage;

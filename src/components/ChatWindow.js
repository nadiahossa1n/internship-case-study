import React, { useState, useEffect, useRef } from "react";
import "./ChatWindow.css";
import { getAIMessage } from "../api/api";
import { marked } from "marked";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowUp, faStop, faRobot } from '@fortawesome/free-solid-svg-icons';

function ChatWindow() {
  const defaultMessage = [{
    role: "assistant",
    content: "Welcome to Bao Distributors! We are a leader in construction and home materials, tools, and appliances. I’m here to help you with product recommendations and any questions you have about our offerings. How can I assist you today?"
  }];

  const quickQuestions = [
    "What brands of drills do you have?",
    "Can you recommend products for bathroom renovation?",
    "I'm looking for a sink. What options do you have?"
  ];

  const [messages, setMessages] = useState(defaultMessage);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (input) => {
    if (input.trim() !== "") {
      // Set user message
      setMessages((prevMessages) => [...prevMessages, { role: "user", content: input }]);
      setInput("");
      setIsLoading(true);

      // Call API & set assistant message
      const newMessage = await getAIMessage(input);
      setIsLoading(false)
      setMessages((prevMessages) => [...prevMessages, newMessage]);
    }
  };

  const handleQuickQuestionClick = (question) => {
    handleSend(question);
  };

  return (
    <div className="messages-container">
      {messages.map((message, index) => (
        <div key={index} className={`${message.role}-message-container`}>
          {message.content && (
            <div className={`message ${message.role}-message`}>
              {message.role === "assistant" && (
                <div className="message-wrapper">
                  <FontAwesomeIcon icon={faRobot} className="bot-icon" />
                  <div 
                    dangerouslySetInnerHTML={{ 
                      __html: marked(message.content).replace(/<p>|<\/p>/g, "") 
                    }} 
                  />
                </div>
              )}
              {message.role === "user" && (
                <div className="user-message-content">
                  <div 
                    dangerouslySetInnerHTML={{ 
                      __html: marked(message.content).replace(/<p>|<\/p>/g, "") 
                    }} 
                  />
                </div>
              )}
            </div>
          )}
        </div>
      ))}

      {messages.length === 1 && (
        <div className="quick-questions">
          {quickQuestions.map((question, index) => (
            <button key={index} onClick={() => handleQuickQuestionClick(question)} className="quick-question-button">
              {question}
            </button>
          ))}
        </div>
      )}

      {isLoading && (
        <div className="assistant-message-container">
          <div className="message assistant-message shimmer-container">
            <div className="shimmer"></div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
          onKeyPress={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              handleSend(input);
              e.preventDefault();
            }
          }}
          rows="3"
        />
        <button
          className="send-button"
          onClick={() => handleSend(input)}
          disabled={!input.trim() || isLoading}
          title={!input.trim() ? "Message is empty" : isLoading ? "Fetching response..." : ""}
        >
          {isLoading ? (
            <FontAwesomeIcon icon={faStop} className="icon" />
          ) : (
            <FontAwesomeIcon icon={faArrowUp} className="icon" />
          )}
        </button>
      </div>
    </div>
  );
}

export default ChatWindow;

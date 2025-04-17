import React, { useState, useEffect, useRef } from "react";
import { Paperclip, Send } from "lucide-react";
import { marked } from "marked";
import { motion, AnimatePresence } from "framer-motion";

export default function ChatBox() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [file, setFile] = useState(null);
  const [showWelcome, setShowWelcome] = useState(true);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = () => {
    if (input.trim() !== "" || file) {
      setShowWelcome(false);
      const userMessage = { text: input, file, role: "user" };
      setMessages((prev) => [...prev, userMessage]);
      setInput("");
      setFile(null);
      setIsTyping(true);

      setTimeout(async () => {
        const reply = await getBotReply(input.trim(), file);
        setMessages((prev) => [...prev, { text: reply, role: "bot" }]);
        setIsTyping(false);
      }, 800);
    }
  };

  const getBotReply = async (msg, file = null) => {
    try {
      const formData = new FormData();

      const formattedHistory = messages.map(m => ({
        role: m.role === "user" ? "user" : "model",
        parts: m.text
      }));
      formData.append("history", JSON.stringify(formattedHistory));

      formData.append("text", msg);
      if (file) formData.append("file", file);

      const res = await fetch("http://localhost:8000/predict", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (data.text_response === "error") {
        return "⚠️ Sorry, something went wrong with the assistant.";
      }

      return data.text_response || "No response.";
    } catch (err) {
      console.error("Fetch Error:", err);
      return "⚠️ Unable to connect to server.";
    }
  };

  return (
    <div className="w-full h-screen flex justify-center items-center bg-gray-50">
      <div className="relative w-full max-w-2xl h-full flex flex-col bg-white shadow-xl rounded-3xl overflow-hidden">
        <AnimatePresence>
          {showWelcome && (
            <motion.div
              key="welcome"
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -30 }}
              transition={{ duration: 0.5 }}
              className="absolute inset-0 flex flex-col items-center justify-center px-4 z-10 bg-white"
            >
              <h1 className="text-2xl md:text-3xl font-semibold mb-6 text-center">
                What can I help with?
              </h1>

              <div className="w-full max-w-xl rounded-full shadow-lg border flex items-center gap-2 px-4 py-2 bg-white">
                <label className="cursor-pointer">
                  <Paperclip className="w-5 h-5 text-gray-500" />
                  <input
                    type="file"
                    className="hidden"
                    onChange={(e) => setFile(e.target.files[0])}
                  />
                </label>

                <input
                  type="text"
                  className="flex-1 text-sm focus:outline-none"
                  placeholder="Ask anything..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) =>
                    e.key === "Enter" && (input.trim() || file) && handleSend()
                  }
                />

                <button
                  onClick={handleSend}
                  disabled={!input.trim() && !file}
                  className={`p-2 rounded-full text-white transition-colors ${
                    input.trim() || file
                      ? "bg-blue-500 hover:bg-blue-600"
                      : "bg-gray-300 cursor-not-allowed"
                  }`}
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>

              {file && (
                <div className="mt-2">
                  <img
                    src={URL.createObjectURL(file)}
                    alt="Mini preview"
                    className="w-16 h-16 object-cover rounded-lg border"
                  />
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Chat interface */}
        {!showWelcome && (
          <div className="flex flex-col h-full w-full">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-white">
              {messages.map((msg, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className={`px-4 py-3 rounded-xl text-sm ${
                    msg.role === "user"
                      ? "bg-blue-100 ml-auto text-right max-w-xs"
                      : "bg-gray-100 mx-auto text-left max-w-lg"
                  }`}
                >
                  {msg.role === "bot" ? (
                    <div
                      className="prose prose-sm"
                      dangerouslySetInnerHTML={{
                        __html: marked.parse(msg.text || ""),
                      }}
                    />
                  ) : (
                    <p>{msg.text}</p>
                  )}

                  {msg.file && msg.role === "user" && (
                    <img
                      src={URL.createObjectURL(msg.file)}
                      alt="Uploaded preview"
                      className="w-24 h-24 object-cover mt-2 rounded-lg border"
                    />
                  )}
                </motion.div>
              ))}

              {/* Typing animation */}
              <AnimatePresence>
                {isTyping && (
                  <motion.div
                    key="typing"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="px-4 py-3 rounded-xl text-sm bg-gray-100 max-w-fit mx-auto text-left"
                  >
                    <span className="animate-pulse text-gray-600">
                      Assistant is typing<span className="animate-bounce">...</span>
                    </span>
                  </motion.div>
                )}
              </AnimatePresence>

              <div ref={messagesEndRef} />
            </div>

            {/* Input bar */}
            <div className="px-4 py-3 bg-white border-t flex-shrink-0">
              <div className="rounded-full shadow-lg border flex items-center gap-2 px-4 py-2">
                <label className="cursor-pointer">
                  <Paperclip className="w-5 h-5 text-gray-500" />
                  <input
                    type="file"
                    className="hidden"
                    onChange={(e) => setFile(e.target.files[0])}
                  />
                </label>

                <input
                  type="text"
                  className="flex-1 text-sm focus:outline-none"
                  placeholder="Ask anything..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) =>
                    e.key === "Enter" && (input.trim() || file) && handleSend()
                  }
                />

                <button
                  onClick={handleSend}
                  disabled={!input.trim() && !file}
                  className={`p-2 rounded-full text-white transition-colors ${
                    input.trim() || file
                      ? "bg-blue-500 hover:bg-blue-600"
                      : "bg-gray-300 cursor-not-allowed"
                  }`}
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>

              {file && (
                <div className="ml-1 mt-2">
                  <img
                    src={URL.createObjectURL(file)}
                    alt="Mini preview"
                    className="w-16 h-16 object-cover rounded-lg border"
                  />
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

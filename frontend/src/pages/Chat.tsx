import { useState, useEffect, useRef, useCallback } from "react";
import { useParams } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import {
  Flex,
  Box,
  Text,
  TextField,
  ScrollArea,
  Heading,
  Button,
  IconButton,
  Spinner,
} from "@radix-ui/themes";
import { CopyIcon } from "@radix-ui/react-icons";
import TypingText from "../components/TypingText";

type Message = { role: "user" | "assistant"; content: string };

export default function Chat({repo_name}: {repo_name: string}) {
  const activeRepo = repo_name;

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = useCallback(async () => {
    const query = input.trim();
    if (!query || !activeRepo || loading) return;

    const userMsg: Message = { role: "user", content: query };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`/api/v1/repo/${activeRepo}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.response || "No response" },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Error fetching response." },
      ]);
    } finally {
      setLoading(false);
    }
  }, [input, activeRepo, loading]);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <Flex direction="column" style={{ height: "100vh" }}>
      {/* Header */}
      <Box p="3" style={{ borderBottom: "1px solid #e5e7eb" }}>
        <Heading size="3" style={{ whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
          {activeRepo || "Chat"}
        </Heading>
      </Box>

      {/* Messages */}
      <ScrollArea style={{ flex: 1 }}>
        <Flex direction="column" gap="3" p="3">
          {messages.length === 0 && (
            <Text color="gray">Ask something about this repo...</Text>
          )}

          {messages.map((msg, idx) => {
            const isUser = msg.role === "user";
            const isLastAssistant =
              !isUser && !loading && idx === messages.length - 1;

            return (
              <Flex key={idx} justify={isUser ? "end" : "start"}>
                <Box
                  p="3"
                  style={{
                    maxWidth: "70%",
                    wordBreak: "break-word",
                    borderRadius: 8,
                    background: isUser ? "#3b82f6" : "#f3f4f6",
                    color: isUser ? "white" : "black",
                  }}
                >
                  {isUser ? (
                    <Text>{msg.content}</Text>
                  ) : (
                    <Box>
                      {isLastAssistant ? (
                        <TypingText text={msg.content} />
                      ) : (
                        <ReactMarkdown>{msg.content}</ReactMarkdown>
                      )}

                      <Flex justify="end" mt="2">
                        <IconButton
                          size="1"
                          onClick={() => copyToClipboard(msg.content)}
                        >
                          <CopyIcon />
                        </IconButton>
                      </Flex>
                    </Box>
                  )}
                </Box>
              </Flex>
            );
          })}

          {loading && (
            <Flex>
              <Spinner />
            </Flex>
          )}

          <div ref={bottomRef} />
        </Flex>
      </ScrollArea>

      {/* Input */}
      <Box p="3" style={{ borderTop: "1px solid #e5e7eb" }}>
        <Flex gap="2">
          <TextField.Root
            placeholder="Type a message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
            style={{ flex: 1 }}
          />

          <Button onClick={sendMessage} disabled={loading || !input.trim()}>
            {loading ? <Spinner size="1" /> : "Send"}
          </Button>
        </Flex>
      </Box>
    </Flex>
  );
}

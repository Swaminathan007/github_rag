import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import {
  Flex,
  Box,
  Text,
  TextField,
  Button,
  ScrollArea,
  Heading,
  IconButton,
  Separator,
  Switch,
  Spinner
} from "@radix-ui/themes";
import { CopyIcon, SunIcon, MoonIcon } from "@radix-ui/react-icons";
import TypingText from "../components/TypingText";

export default function ChatApp() {
  const [repos, setRepos] = useState<string[]>([]);
  const [activeRepo, setActiveRepo] = useState<string>("");

  const [messages, setMessages] = useState<
    { role: string; content: string }[]
  >([]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const [theme, setTheme] = useState<"light" | "dark">("light");

  const bottomRef = useRef<HTMLDivElement | null>(null);

  /* Load theme */
  useEffect(() => {
    const saved = localStorage.getItem("theme") as
      | "light"
      | "dark"
      | null;
    if (saved) setTheme(saved);
  }, []);

  /* Persist theme */
  useEffect(() => {
    localStorage.setItem("theme", theme);
  }, [theme]);

  /* Fetch repos */
  useEffect(() => {
    fetch("/api/v1/repo/get_all_repos")
      .then((res) => res.json())
      .then((data) => {
        const list = data.collection_list || [];
        setRepos(list);
        if (list.length > 0) setActiveRepo(list[0]);
      });
  }, []);

  /* Auto scroll */
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async () => {
    if (!input.trim() || !activeRepo) return;

    const newMessages = [...messages, { role: "user", content: input }];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`/api/v1/repo/${activeRepo}/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: input }),
      });

      const data = await res.json();

      setMessages([
        ...newMessages,
        { role: "assistant", content: data.response || "No response" },
      ]);
    } catch {
      setMessages([
        ...newMessages,
        { role: "assistant", content: "Error fetching response." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    console.log("copying",text)
    navigator.clipboard.writeText(text);
  };

  return (
    <Flex style={{ height: "100vh" }}>
      {/* Sidebar */}
      <Box
        style={{
          width: "260px",
          borderRight: "1px solid var(--gray-6)",
          padding: "16px",
        }}
      >
        <Heading size="4" mb="3">
          Repos
        </Heading>

        <Flex direction="column" gap="2">
          {repos.map((repo) => (
            <Button
              key={repo}
              variant={repo === activeRepo ? "solid" : "soft"}
              onClick={() => {
                setActiveRepo(repo);
                setMessages([]);
              }}
            >
              {repo}
            </Button>
          ))}
        </Flex>

        <Separator my="4" />

        <Flex align="center" justify="between">
          <Text size="2">Dark Mode</Text>
          <Switch
            checked={theme === "dark"}
            onCheckedChange={(val) =>
              setTheme(val ? "dark" : "light")
            }
          />
        </Flex>
      </Box>

      {/* Chat */}
      <Flex direction="column" style={{ flex: 1 }}>
        {/* Header */}
        <Box
          style={{
            padding: "14px 20px",
            borderBottom: "1px solid var(--gray-6)",
          }}
        >
          <Flex align="center" justify="between">
            <Heading size="4">
              {activeRepo || "Select a repo"}
            </Heading>

            <IconButton
              variant="soft"
              onClick={() =>
                setTheme(theme === "dark" ? "light" : "dark")
              }
            >
              {theme === "dark" ? <SunIcon /> : <MoonIcon />}
            </IconButton>
          </Flex>
        </Box>

        {/* Messages */}
        <ScrollArea style={{ flex: 1 }}>
          <Flex direction="column" gap="3" p="4">
            {messages.map((msg, idx) => {
              const isLast = idx === messages.length - 1;

              return (
                <Flex
                  key={idx}
                  justify={msg.role === "user" ? "end" : "start"}
                >
                  <Box
                    style={{
                      maxWidth: "70%",
                      padding: "12px",
                      borderRadius: "12px",
                      background:
                        msg.role === "user"
                          ? "var(--accent-9)"
                          : "var(--color-panel)",
                      color:
                        msg.role === "user"
                          ? "white"
                          : "var(--gray-12)",
                      border:
                        msg.role === "assistant"
                          ? "1px solid var(--gray-6)"
                          : "none",
                    }}
                  >
                    {msg.role === "assistant" ? (
                      isLast ? (
                        <TypingText text={msg.content} />
                      ) : (
                        <ReactMarkdown>{msg.content}</ReactMarkdown>
                      )
                    ) : (
                      <Text>{msg.content}</Text>
                    )}

                    {msg.role === "assistant" && (
                      <Flex justify="end" mt="2">
                        <IconButton
                          size="1"
                          variant="ghost"
                          onClick={() =>
                            copyToClipboard(msg.content)
                          }
                        >
                          <CopyIcon />
                        </IconButton>
                      </Flex>
                    )}
                  </Box>
                </Flex>
              );
            })}

            {loading && (
                <Flex>
                    <Spinner/>
                    <Text size="1" color="gray">
                        Thinking...
                    </Text>
                </Flex>
            )}

            <div ref={bottomRef} />
          </Flex>
        </ScrollArea>

        <Separator />

        {/* Input */}
        <Box p="3">
          <Flex gap="2">
            <TextField.Root
              placeholder="Ask something..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              style={{ flex: 1 }}
            />
            <Button onClick={sendMessage} disabled={loading}>
              Send
            </Button>
          </Flex>
        </Box>
      </Flex>
    </Flex>
  );
}
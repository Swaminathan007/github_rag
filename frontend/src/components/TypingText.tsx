import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";

export default function TypingText({ text }: { text: string }) {
  const [displayed, setDisplayed] = useState("");

  useEffect(() => {
    let i = 0;
    setDisplayed("");

    const interval = setInterval(() => {
      i++;
      setDisplayed(text.slice(0, i));
      if (i >= text.length) clearInterval(interval);
    }, 10); // speed (lower = faster)

    return () => clearInterval(interval);
  }, [text]);

  return <ReactMarkdown>{displayed}</ReactMarkdown>;
}
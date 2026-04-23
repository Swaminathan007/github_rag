import { useState } from "react";
import {
  Flex,
  Box,
  Heading,
  Text,
  TextField,
  Button,
  Spinner,
  Card
} from "@radix-ui/themes";

export default function Home() {
  const [repoUrl, setRepoUrl] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!repoUrl.trim()) return;

    setLoading(true);
    try {
      const res = await fetch("/api/v1/repo/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_url: repoUrl }),
      });

      const data = await res.json();
      console.log(data);

      setRepoUrl("");
      window.location.href = "/repos";
    } catch (err) {
      console.log(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Flex
      align="center"
      justify="center"
      style={{ height: "100vh", padding: "16px" }}
    >
      <Card style={{ width: 420 }}>
        <Flex direction="column" gap="4">
          <Box>
            <Heading size="5">GitHub Insights</Heading>
            <Text color="gray" size="2">
              Chat with any repository
            </Text>
          </Box>

          <Flex direction="column" gap="2">
            <Text size="1" weight="bold">
              Repository URL
            </Text>
            <TextField.Root
              placeholder="https://github.com/user/repo"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleSubmit();
              }}
            />
          </Flex>

          <Button
            onClick={handleSubmit}
            disabled={loading || !repoUrl.trim()}
          >
            {loading ? (
              <Flex align="center" gap="2">
                <Spinner size="1" />
                Adding...
              </Flex>
            ) : (
              "Add Repository"
            )}
          </Button>
          <Button
            onClick={() => window.location.href = "/repos"}
          >
            Go to repo page
          </Button>
        </Flex>
      </Card>
    </Flex>
  );
}
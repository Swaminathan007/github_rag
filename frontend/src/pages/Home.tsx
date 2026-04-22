import {
  Flex,
  Text,
  Button,
  Card,
  Dialog,
  TextField,
  Heading,
  Separator,
  Badge
} from "@radix-ui/themes";
import { useEffect, useState } from "react";

export default function Home() {
  const [repos, setRepos] = useState([]);
  const [repoUrl, setRepoUrl] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch("/api/v1/repo/get_all_repos")
      .then((res) => res.json())
      .then((data) => {
        setRepos(data.collection_list || []);
      })
      .catch((err) => console.log(err));
  }, []);

  const handleSubmit = async () => {
    if (!repoUrl) return;

    setLoading(true);
    try {
      const res = await fetch("/api/v1/repo/add", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ repo_url: repoUrl }),
      });

      const data = await res.json();
      console.log(data);

      // refresh repo list
      const updated = await fetch("/api/v1/repo/get_all_repos");
      const updatedData = await updated.json();
      setRepos(updatedData.collection_list || []);

      setRepoUrl("");
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
      style={{
        minHeight: "100vh",
        background: "linear-gradient(to bottom right, #0f172a, #1e293b)",
      }}
    >
      <Card
        size="4"
        style={{
          width: "420px",
          padding: "28px",
          borderRadius: "16px",
        }}
      >
        <Flex direction="column" gap="4">
          {/* Header */}
          <Heading align="center" size="6">
            GitHub RAG
          </Heading>
          <Text align="center" color="gray">
            Get insights from your repositories
          </Text>

          <Separator size="4" />

          {/* Input */}
          <Flex direction="column" gap="2">
            <Text size="2" weight="medium">
              Repository URL
            </Text>
            <TextField.Root
              placeholder="https://github.com/user/repo"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
            />
          </Flex>

          {/* Submit */}
          <Button
            size="3"
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading ? "Adding..." : "Add Repository"}
          </Button>

          {/* Repo List */}
          <Flex direction="column" gap="2">
            <Text size="2" weight="medium">
              Your Repositories
            </Text>

            <Flex wrap="wrap" gap="2">
              {repos.length === 0 && (
                <Text size="1" color="gray">
                  No repositories added yet
                </Text>
              )}

              {repos.map((repo, index) => (
                <Badge key={index} variant="soft">
                  {repo}
                </Badge>
              ))}
            </Flex>
          </Flex>

          {/* Dialog */}
          <Dialog.Root>
            <Dialog.Trigger>
              <Button variant="soft">What is this?</Button>
            </Dialog.Trigger>

            <Dialog.Content style={{ maxWidth: 400 }}>
              <Dialog.Title>About</Dialog.Title>
              <Dialog.Description>
                This tool lets you add GitHub repositories and generate insights
                using RAG (Retrieval-Augmented Generation).
              </Dialog.Description>

              <Flex gap="3" mt="4" justify="end">
                <Dialog.Close>
                  <Button>Got it</Button>
                </Dialog.Close>
              </Flex>
            </Dialog.Content>
          </Dialog.Root>
        </Flex>
      </Card>
    </Flex>
  );
}
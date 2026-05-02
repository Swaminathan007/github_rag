import { useState } from "react";
import {
  Flex,
  Box,
  Heading,
  Text,
  TextField,
  Button,
  Spinner,
  Card,
  Callout,
  IconButton
} from "@radix-ui/themes";
import { GearIcon } from "@radix-ui/react-icons";

export default function Home() {
  const [repoUrl, setRepoUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [branch, setBranch] = useState("");

  const handleSubmit = async () => {
    if (!repoUrl.trim()) return;

    setLoading(true);
    try {
      const res = await fetch("/api/v1/repo/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_url: repoUrl,branch: branch }),
      });

      const data = await res.json();
      
      setRepoUrl("");
      setBranch("");
      if(data.code != 201){
        setMessage(data.response);
        return;
      }
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
         {message && (
          <Callout.Root color="gray">
            <Callout.Text>{message}</Callout.Text>
          </Callout.Root>
         )}
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

          <Flex direction="column" gap="2">
            <Text size="1" weight="bold">
              Branch
            </Text>
            <TextField.Root
              placeholder="main"
              value={branch}
              onChange={(e) => setBranch(e.target.value)}
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
            View Repositories
          </Button>
          <Button
            onClick={() => window.location.href = "/settings"}
          >
            Settings <IconButton>
              <GearIcon />
            </IconButton>
          </Button>
        </Flex>
      </Card>
    </Flex>
  );
}
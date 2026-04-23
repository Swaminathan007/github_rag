import {
  Flex,
  Text,
  Heading,
  Card,
  Spinner,
  ScrollArea,
  IconButton,
  AlertDialog,
  Button,
  Callout
} from "@radix-ui/themes";
import { TrashIcon } from "@radix-ui/react-icons";
import { useEffect, useState } from "react";

export default function Repos() {
  const [repos, setRepos] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/v1/repo/get_all_repos")
      .then((res) => res.json())
      .then((data) => {
        const list = data.collection_list || [];
        setRepos(list);
      })
      .finally(() => setLoading(false));
  }, [loading]);

  const handleRepoClick = (repo: string) => {
    window.location.href = `/chat/${repo}`;
  };

  const handleDelete = (repo: string) => {
    setLoading(true);
    setMessage(null);

    fetch(`/api/v1/repo/delete/${repo}`, {
      method: "DELETE",
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.response === `${repo} deleted successfully`) {
          setRepos((prev) => prev.filter((r) => r !== repo));
          setMessage("Repository deleted successfully");
        } else {
          setMessage("Failed to delete repository");
        }
      })
      .catch(() => setMessage("Error deleting repository"))
      .finally(() => {
        setLoading(false);
        setDeleteTarget(null);
      });
  };

  return (
    <Flex align="center" justify="center" style={{ height: "100vh", padding: "16px" }}>
      <Card style={{ width: 480 }}>
        <Flex direction="column" gap="4">
          {/* Header */}
          <Flex direction="column" gap="1">
            <Heading size="5">Repositories</Heading>
            <Text color="gray" size="2">
              Select a repository to start chatting
            </Text>
          </Flex>

          {/* Feedback message */}
          {message && (
            <Callout.Root color="gray">
              <Callout.Text>{message}</Callout.Text>
            </Callout.Root>
          )}

          {/* Content */}
          {loading ? (
            <Flex align="center" justify="center" py="6" gap="2">
              <Spinner />
              <Text size="2" color="gray">
                Loading...
              </Text>
            </Flex>
          ) : repos.length === 0 ? (
            <Flex direction="column" align="center" py="6" gap="2">
              <Text color="gray">No repositories found</Text>
            </Flex>
          ) : (
            <ScrollArea style={{ maxHeight: 320 }}>
              <Flex direction="column" gap="2" pr="2">
                {repos.map((repo) => (
                  <Card
                    key={repo}
                    onClick={() => handleRepoClick(repo)}
                    style={{ cursor: "pointer" }}
                  >
                    <Flex align="center" justify="between">
                      <Text size="2" style={{ wordBreak: "break-all" }}>
                        {repo}
                      </Text>

                      <IconButton
                        color="red"
                        onClick={(e) => {
                          e.stopPropagation();
                          setDeleteTarget(repo);
                        }}
                      >
                        <TrashIcon />
                      </IconButton>
                    </Flex>
                  </Card>
                ))}
              </Flex>
            </ScrollArea>
          )}

          {/* Footer */}
          {!loading && repos.length > 0 && (
            <Flex justify="between">
              <Text size="1" color="gray">
                {repos.length} repo{repos.length !== 1 ? "s" : ""}
              </Text>
              <Text size="1" color="gray">
                click to open
              </Text>
            </Flex>
          )}
        </Flex>
      </Card>

      {/* Confirm Dialog */}
      <AlertDialog.Root open={!!deleteTarget} onOpenChange={() => setDeleteTarget(null)}>
        <AlertDialog.Content>
          <AlertDialog.Title>Delete repository?</AlertDialog.Title>
          <AlertDialog.Description>
            This action cannot be undone. This will permanently delete the repository.
          </AlertDialog.Description>

          <Flex gap="3" mt="4" justify="end">
            <AlertDialog.Cancel>
              <Button variant="soft" color="gray">Cancel</Button>
            </AlertDialog.Cancel>
            <AlertDialog.Action>
              <Button
                color="red"
                onClick={() => deleteTarget && handleDelete(deleteTarget)}
              >
                Delete
              </Button>
            </AlertDialog.Action>
          </Flex>
        </AlertDialog.Content>
      </AlertDialog.Root>
    </Flex>
  );
}

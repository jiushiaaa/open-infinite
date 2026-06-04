import { AppShell } from "./components/AppShell";
import { StoryEntryPage } from "./components/StoryEntryPage";
import { WorkspacePage } from "./components/WorkspacePage";
import { WorldAnchorPage } from "./components/WorldAnchorPage";
import { ImportNovelPage } from "./components/ImportNovelPage";
import { GenesisPage } from "./components/GenesisPage";
import { WorldSandboxPage } from "./components/WorldSandboxPage";
import { TianmingPage } from "./components/TianmingPage";
import { CharacterLensPage } from "./components/CharacterLensPage";
import { AuthorAdoptionPage } from "./components/AuthorAdoptionPage";
import { useRoute } from "./routing";

export function App() {
  const route = useRoute();
  return (
    <AppShell route={route}>
      {route.name === "workspace" && <WorkspacePage slug={route.slug} />}
      {route.name === "sandbox" && <WorldSandboxPage slug={route.slug} />}
      {route.name === "tianming" && <TianmingPage slug={route.slug} />}
      {route.name === "lens" && <CharacterLensPage slug={route.slug} />}
      {route.name === "author" && <AuthorAdoptionPage slug={route.slug} />}
      {route.name === "anchor" && <WorldAnchorPage slug={route.slug} />}
      {route.name === "import" && <ImportNovelPage />}
      {route.name === "genesis" && <GenesisPage />}
      {route.name === "entry" && <StoryEntryPage />}
    </AppShell>
  );
}

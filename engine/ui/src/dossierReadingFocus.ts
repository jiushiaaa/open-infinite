interface DossierReadingFocusSection {
  id: string;
  title?: string;
  viewpoint?: string;
  narrative_role?: string;
  evidence_refs?: string[];
  evidence_mode?: {
    refs?: string[];
  };
}

export interface DossierReadingFocusInput {
  sections: DossierReadingFocusSection[];
  activeSectionId: string;
  totalEvidenceCount: number;
  misbeliefCount: number;
}

export interface DossierReadingFocus {
  currentIndex: number;
  positionLabel: string;
  title: string;
  roleLabel: string;
  evidenceLabel: string;
  misbeliefLabel: string;
  previousSectionId: string | null;
  nextSectionId: string | null;
}

function evidenceRefs(section: DossierReadingFocusSection): string[] {
  const refs = section.evidence_mode?.refs?.length
    ? section.evidence_mode.refs
    : section.evidence_refs || [];
  return refs.filter((ref) => ref.trim().length > 0);
}

export function deriveDossierReadingFocus(
  input: DossierReadingFocusInput,
): DossierReadingFocus | null {
  if (input.sections.length === 0) return null;
  const activeIndex = input.sections.findIndex((section) => section.id === input.activeSectionId);
  const currentIndex = activeIndex >= 0 ? activeIndex : 0;
  const section = input.sections[currentIndex];
  const sectionEvidenceCount = evidenceRefs(section).length;
  const evidenceLabel =
    input.totalEvidenceCount > 0 && input.totalEvidenceCount !== sectionEvidenceCount
      ? `本场 ${sectionEvidenceCount} 条证据 · 全卷 ${input.totalEvidenceCount} 条`
      : `本场 ${sectionEvidenceCount} 条证据`;

  return {
    currentIndex,
    positionLabel: `${String(currentIndex + 1).padStart(2, "0")} / ${String(
      input.sections.length,
    ).padStart(2, "0")}`,
    title: section.title?.trim() || `第 ${currentIndex + 1} 场`,
    roleLabel: section.viewpoint?.trim() || section.narrative_role?.trim() || "正文场景",
    evidenceLabel,
    misbeliefLabel:
      input.misbeliefCount > 0 ? `${input.misbeliefCount} 条误会可追` : "暂无误会图谱",
    previousSectionId: input.sections[currentIndex - 1]?.id || null,
    nextSectionId: input.sections[currentIndex + 1]?.id || null,
  };
}

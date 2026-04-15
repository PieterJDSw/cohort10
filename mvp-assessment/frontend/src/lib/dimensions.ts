const DIMENSION_LABELS: Record<string, string> = {
  coding_skill: 'Coding Skill',
  architecture_design: 'Architecture',
  core_understanding: 'Core Understanding',
  communication: 'Communication',
  ownership_judgment: 'Ownership Judgment',
  ai_fluency: 'AI Fluency',
}

export function formatDimensionLabel(value: string) {
  return (
    DIMENSION_LABELS[value] ??
    value
      .split('_')
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
      .join(' ')
  )
}

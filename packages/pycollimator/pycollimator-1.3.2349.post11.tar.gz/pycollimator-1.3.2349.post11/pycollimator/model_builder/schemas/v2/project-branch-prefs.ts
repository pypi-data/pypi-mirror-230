// ProjectBranchPrefsV1

// Per-user preferences for a project branch view.
// Prefs entity id: project_uuid.
export interface ProjectBranchPrefsV1 {
  selected_branch_name?: string;
}

// Note: this must be manually copied in Go.
export const PROJECT_BRANCH_PREFS_V1_KEY = 'PROJECT_BRANCH_PREFS_V1';

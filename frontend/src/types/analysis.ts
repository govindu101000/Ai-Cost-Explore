export interface Issue {
  resource_name: string;
  resource_type: string;
  issue_type: string;
  severity: "high" | "medium" | "low";
  description: string;
  business_impact: string;
  recommendation: string;
  estimated_savings: string;
  fix_command: string;
  best_practice: string;
}

export interface Analysis {
  id: number;
  resource_group: string;
  resources_scanned: number;
  issues_found: number;
  estimated_savings: string;
  created_at: string;
  analysis_result: {
    summary: string;
    estimated_total_monthly_savings: string;
    issues: Issue[];
  };
}
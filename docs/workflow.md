# 🔄 Project Workflow – Retail Management System

This document outlines the step-by-step workflow for starting and running the project, including which markdown files to update at each stage. Use this as a quick reference to ensure consistency and focus.

---

## 1. Preparation
- Review `NEW_PRD.md`, `implementation_plan.md`, and `PROJECT_RULES.md`.
- Ensure all stakeholders understand the project scope, rules, and plan.

## 2. Initial Project Setup
- Initialize Git repository and project structure.
- Add all core markdown files to the repo root:
  - `NEW_PRD.md`
  - `implementation_plan.md`
  - `PROJECT_RULES.md`
  - `PROJECT_CHECKLIST.md`
  - `step_and_summary.md`
  - `workflow.md` (this file)
- Set up a basic `README.md` with project overview and links to the above files.

## 3. Checklist Creation
- Populate `PROJECT_CHECKLIST.md` with actionable items from the implementation plan.
- Mark the first step as "in progress".

## 4. Planning Before Coding
- For each major feature/module, write a detailed plan and add it to the checklist.
- Wait for stakeholder approval before starting implementation.

## 5. Implementation (Iterative)
- After approval, implement the planned step.
- As soon as a step is completed:
  - Update `PROJECT_CHECKLIST.md` (mark as complete, add next steps).
  - Update `step_and_summary.md` (summarize what was done, suggest improvements).
- Before starting the next step, repeat the planning/approval process.
- Sync status UI step fully completed and documented (see checklist and step_and_summary.md)
- UAT testing for backend sync features completed successfully - device registration, disconnect/reconnect, and error handling all validated

## 6. Continuous Documentation
- If any rules, requirements, or plans change, immediately update the relevant markdown files:
  - `PROJECT_RULES.md`
  - `NEW_PRD.md`
  - `implementation_plan.md`
  - `PROJECT_CHECKLIST.md`
  - `step_and_summary.md`
  - `workflow.md`

## 7. Review & Feedback
- Regularly review progress with stakeholders using the checklist and summaries.
- Adjust the plan as needed, always updating documentation.

---

*Always keep all markdown files up to date to maintain focus, transparency, and alignment throughout the project.* 

## Assistant Task Rule
- When the user asks "where are we" or "what's next":
  1. Review docs/PROJECT_CHECKLIST.md, step_and_summary.md, workflow.md, and CHANGELOG.md.
  2. Provide a detailed update of:
     - What has been completed
     - What is currently in progress
     - What the next step is
  3. Strictly follow this process every time, so the user always gets a clear, up-to-date project status. 
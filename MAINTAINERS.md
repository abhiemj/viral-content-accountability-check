# Maintainer guide — securing `main` & accepting contributions

This repo is set up so anyone can contribute, but nothing lands on `main`
without review and passing tests. Here's how to lock it down after you push.

## 1. Push the repo, then make it public

First create an **empty** repo named `viral-videos-accountability-check` on
GitHub (no README/license — this repo already has them), then:

```bash
git branch -M main
git remote add origin https://github.com/abhiemj/viral-videos-accountability-check.git
git push -u origin main
```

Then on GitHub: **Settings → General → Danger Zone → Change visibility → Public**
(so developers can find and fork it).

## 2. Protect the `main` branch

GitHub → your repo → **Settings → Branches → Add branch ruleset**
(or "Add rule" under *Branch protection rules*). Target branch: `main`.

Enable these:

| Setting | Why |
|---|---|
| **Require a pull request before merging** | No direct pushes to `main`. |
| ↳ **Require approvals: 1** | At least one reviewer must approve. |
| ↳ **Dismiss stale approvals on new commits** | Re-review after changes. |
| ↳ **Require review from Code Owners** | You (via CODEOWNERS) auto-review. |
| **Require status checks to pass** | PR can't merge until CI is green. |
| ↳ Select the check: **`Tests (Python 3.x)`** | The CI job from `ci.yml`. |
| ↳ **Require branches to be up to date** | Re-test against latest `main`. |
| **Require conversation resolution** | All review comments resolved first. |
| **Block force pushes** | History can't be rewritten. |
| **Restrict deletions** | `main` can't be deleted. |

Optional, stricter:
- **Require signed commits** — commits must be GPG/SSH-signed.
- **Require linear history** — squash/rebase merges only, no merge commits.
- **Include administrators** — the rules apply to you too (recommended once
  you have collaborators).

> The status check only appears in the list **after CI has run at least once**,
> so push the repo (which triggers CI) before configuring required checks.

## 3. How people contribute (no write access needed)

External contributors **fork → branch → PR**. They never need push access to
your repo. Their PR:

1. Runs CI automatically (tests on Python 3.10–3.12).
2. Requests your review (via CODEOWNERS).
3. Can be merged only when **CI is green + you approve**.

You review in the GitHub UI, request changes or approve, then **Squash and
merge**.

## 4. Giving trusted people more access (optional)

**Settings → Collaborators and teams** → add people with a role:
- **Triage** — manage issues/PRs, no code write.
- **Write** — push to non-protected branches, still can't bypass `main` rules.
- **Maintain** — manage most settings, not destructive ones.

Even collaborators go through PRs — branch protection still applies.

## 5. Good hygiene

- Label issues (`good first issue`, `help wanted`) to attract contributors.
- Enable **Settings → General → Discussions** for design conversations.
- Consider **Dependabot** (Settings → Code security) for dependency updates.
- Never merge a PR that adds a secret or removes source citations from verdict
  logic (see the ground rules in [CONTRIBUTING.md](CONTRIBUTING.md)).

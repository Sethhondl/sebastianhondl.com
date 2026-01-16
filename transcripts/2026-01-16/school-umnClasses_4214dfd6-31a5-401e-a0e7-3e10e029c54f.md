# Claude Conversation Transcript

---

## User [2026-01-16T14:12:28.611Z]

I'd like to make a CloudMD file for my directed study. The first initial things I'd like to put on there is the git etiquette that this research group uses. You can find it hear. github.com/Serverson-group/serverson_group_git

## Assistant [2026-01-16T14:12:33.160Z]



## Assistant [2026-01-16T14:12:33.425Z]

I'll fetch the git etiquette information from that GitHub repository.

## Assistant [2026-01-16T14:12:34.690Z]



## User [2026-01-16T14:12:35.474Z]

[Tool Error: Request failed with status code 404]

## Assistant [2026-01-16T14:12:39.812Z]



## Assistant [2026-01-16T14:12:40.479Z]

The URL returned a 404 error - the repository wasn't found. This could be because:

1. The repository or organization name might be spelled differently
2. It might be a private repository (which I can't access)
3. The URL might have a typo

Could you double-check the URL? If it's a private repo, you could copy the content from the README or relevant files and share it with me directly.

## User [2026-01-16T14:13:06.094Z]

its https://github.com/Severson-Group/severson_group_git

## Assistant [2026-01-16T14:13:09.252Z]



## Assistant [2026-01-16T14:13:10.164Z]



## User [2026-01-16T14:13:18.418Z]

[Tool Result: # Git Etiquette, Guidelines, and Best Practices

## Commit Standards

**Message Structure:**
- Maximum line length: 72 characters
- Blank line between paragraphs and bulleted lists
- Use imperative present tense: "make xyzzy do frotz" rather than "makes xyzzy" or "I changed xyzzy"

**Philosophy:** Commits should read as instructions to the codebase about what changes occur, maintaining clarity for future readers.

## Branch Strategy

**Long-Running Branches:**
- `master`: Stable release branch. Only maintainers commit via pull requests from `develop`. Represents the latest official release.
- `develop`: Stable beta branch. Only maintainers commit via pull requests from topic branches. Current development work sits here.

**Topic Branches:** Developers create feature/bug-fix branches from `develop` or other topic branches. Names should clearly indicate the work being addressed.

## Collaboration Workflow

1. Developer creates topic branch from `develop`
2. Developer commits work locally, then pushes frequently to server (backup + visibility)
3. Developer creates pull request when ready to merge
4. Maintainers and peers review via GitHub comments
5. Maintainers complete the PR, delete the topic branch
6. Developer runs `git remote update origin --prune` locally, then deletes their local branches

## Pull Request Standards

Effective PRs should:
- Represent self-contained, reviewable changesets
- Use clear, descriptive titles
- Include descriptions explaining *what* changed and *why*
- Provide all context needed for review (screenshots, PDFs, etc.)
- Assign reviewers and specify feedback desired
- Link to related issues
- Use markdown formatting

## Critical Restrictions

- Never rebase, squash, or amend commits already pushed to the server
- Use simple, informative topic branch names
- Mark major releases with tags
- Include README.md in repositories with relevant project information

## Debugging & Investigation

Developers should use `git blame` to review who last modified each line, helping trace decision-making and identify contributors.]

## Assistant [2026-01-16T14:13:23.683Z]



## Assistant [2026-01-16T14:13:24.287Z]

Got it. Now let me create a markdown file for your directed study with this git etiquette information.

## Assistant [2026-01-16T14:13:28.302Z]



## User [2026-01-16T14:13:28.535Z]

[Tool Result: File created successfully at: /Users/sethhondl/dev/school/umnClasses/DirectedStudyElev/directed_study.md]

## Assistant [2026-01-16T14:13:32.842Z]



## Assistant [2026-01-16T14:13:34.415Z]

Done. I created `directed_study.md` with the Severson Group git etiquette including:

- Commit message standards (72 char limit, imperative tense)
- Branch strategy (`master`, `develop`, topic branches)
- Collaboration workflow (6-step process)
- Pull request standards
- Critical restrictions (never rebase pushed commits, etc.)
- Debugging tips (`git blame`)

Let me know what else you'd like to add to it.


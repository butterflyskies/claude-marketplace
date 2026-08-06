# Repository setup

Use this reference only when the user explicitly requests creation or configuration of a repository. It is not standing authorization for GitHub writes.

## Shape

- discover the default branch and existing repository conventions;
- use a feature branch rather than committing directly to the default branch;
- configure formatting, lint, tests, and build checks that mirror local verification;
- prefer linear history and prohibit force-pushes to protected branches when that matches the repository's governance; and
- document required secrets without committing them.

Repository rules, branch protection, CI creation, Pages, commits, pushes, pull requests, merges, and deployments are separate external mutations. Perform only the exact actions the user or repository authority explicitly authorizes. Verify the authenticated actor on the exact write path first.

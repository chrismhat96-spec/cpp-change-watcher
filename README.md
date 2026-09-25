# C++ Change Watcher

A separate daily watcher for **C++ itself and the MSVC C++ toolchain**.

It monitors:
- Microsoft MSVC What's New
- Microsoft C/C++ language conformance
- MSVC conformance, behavior changes, and bug fixes
- MSVC compiler/toolset version changes
- Visual Studio release notes
- ISO/IEC JTC1/SC22/WG21 C++ committee papers

When one of those sources changes, the watcher emails **chrismhat96@gmail.com** through Resend.

## One-time setup

This repository needs its own GitHub Actions secret. GitHub repository secrets are not automatically shared between separate repositories.

Open **Settings → Secrets and variables → Actions → New repository secret** and create:

`RESEND_API_KEY`

Use the same Resend API key you used for the Windows API watcher.

Then open **Actions → C++ Change Watcher → Run workflow**.

The first run establishes the baseline and intentionally sends no email. Future runs email only when a monitored source changes.

## Gmail

Gmail is receive-only. This repository never logs into Google and does not need your Gmail password, Google App Password, or Google 2FA.

## Schedule

Runs daily at 13:37 UTC. The runner is pinned to Ubuntu 24.04 so a future change to GitHub's `ubuntu-latest` label does not affect this workflow.

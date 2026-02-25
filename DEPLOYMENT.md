Deployment - Create a GitHub release
===================================

This project includes a GitHub Actions workflow that will create a repository release and upload a ZIP of the repository whenever you push a tag matching `v*` (for example `v1.2.0`).

How to create a release locally:

1. Create an annotated tag (replace `v1.2.3` with the new version):

```bash
git tag -a v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3
```

2. GitHub Actions will run the workflow at `.github/workflows/release.yml` and create a release named `v1.2.3` with an uploaded ZIP asset.

Notes:
- The workflow uses the automatically-provided `GITHUB_TOKEN` so no extra secrets are required for basic releases.
- If you want the workflow to build artifacts (Android APK, Python wheel, docs, etc.) before uploading, I can update the workflow to run build steps.

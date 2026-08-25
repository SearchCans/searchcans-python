# SearchCans Python SDK

The official Python SDK for SearchCans gives Python applications a small, explicit interface for three authenticated APIs:

- **SERP API** for Google, Bing, and supported Google vertical engines.
- **Reader API** for web extraction, file extraction, and screenshots.
- **Account API** for credit and parallel-lane pre-flight checks.

The SDK returns the original successful API envelope and adds typed account models and typed errors. It does not hide billable retries or turn a one-time SERP response into a ranking or monitoring claim.

## Install

Until the first PyPI publication, install the tagged GitHub release:

```bash
pip install "git+https://github.com/SearchCans/searchcans-python.git@v0.1.0"
```

Then set your key outside source control:

```bash
export SEARCHCANS_API_KEY="your_api_key"
```

Continue with the [Quickstart](quickstart.md).

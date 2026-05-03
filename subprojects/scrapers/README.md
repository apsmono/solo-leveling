# Sub-Project: Scrapers

Python automation scripts for data collection and processing.

## Conventions

- Each scraper lives in its own subdirectory.
- Include a `requirements.txt` if external dependencies are needed.
- Accept configuration via environment variables or CLI args.
- Log to stdout; the orchestrator (brain scheduler or cron) handles persistence.

## Example

```bash
cd subprojects/scrapers
pip install -r requirements.txt
python example_scraper/main.py --target https://example.com
```

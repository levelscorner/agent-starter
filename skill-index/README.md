# Skill index

`index.json` is one record per skill or command (1,041 today: 1,009 installed items plus 32 house drafts). Code filters it with zero model tokens; agents never read it whole.

Each record: `name`, `source` (`house`, `library`, `claude-skills`, `claude-commands`, `claude-plugin:<name>`), `kind`, `category` (1 Engineering spine, 2 Money path, 3 Growth layer, 4 Glue, 5 Product and UI, 6 Unmapped / other), `area`, `confidence` of that category, `tags` (dev or non-dev, technical or non-technical), `keywords`, `status` (house, library, other, quarantined) with `status_reason`, `precedence` (2 house, 3 library, 4 other, 5 quarantined; 1 is the owner's rules), a description of 200 characters or less, `load` (the file under its source) and `hash` of that file.

- Rebuild: `python3 tools/build_skill_index.py --catalog <catalog.json>`. Only changed records are rewritten.
- Use: `python3 tools/select_skills.py "<problem>"`. See [skills/skill-selector](../skills/skill-selector/SKILL.md).
- No local paths or private repo names go in; the generator refuses them.

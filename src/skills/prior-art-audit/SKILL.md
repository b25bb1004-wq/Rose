---
name: prior-art-audit
description: Check whether a research or competition idea is already published before claiming novelty, with cheap verified citations. Use before scoring novelty, naming a lead contribution, writing a "what is new" section, or trusting another agent's literature claims.
quality: Planning
---
# Prior-art audit
1. **Read the rubric first** if the idea is being judged: what counts as novel at each level, and what else earns credit (efficiency, negative results, controlled studies).
2. **Search the claim, not the topic.** One search per claim, phrased as the sentence you would put in the report; several searches in one turn. Expect recent preprints that collide.
3. **Verify ids and read abstracts cheaply:** `curl -s -L "https://export.arxiv.org/api/query?id_list=ID1,ID2&max_results=100"` (https and `-L`; plain http returns nothing and every id looks fake). Parse `<title>`, `<published>`, `<summary>`. A batch of 70 ids is one call; sleep 3 s between separate calls.
4. **Tag every claim:** `[abs]` abstract read, `[search]` summary only, `[mem]` unchecked. Keep a `refs_verified.txt`. "None found" means searches were run, not that a review was done; say so.
5. **Open the abstract before repeating any number** another agent cites; misquoted conditions are common.
6. **Re-score novelty after the search** and recompute weighted tables by script, not by hand.
7. **Output:** claim | nearest prior art with id and date | what is left | level. When the method is crowded, reframe the contribution as a controlled study or a protocol insight.
8. **Search before building a test.** If the failure you want to measure is a known one, a published benchmark probably exists; find it first. Never claim "a paper proves X" without finding it; report that none exists and offer the narrower true claim.
9. **Read the full text, not only the abstract,** when the argument depends on it. `pdftotext -layout paper.pdf out.txt`, then grep for "Table", model names and "limitation".

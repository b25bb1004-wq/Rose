---
name: eval-harness-sanity-check
description: Before trusting or waiting on any benchmark or scoring script, run it on 10 to 25 items and check the score is plausible. Use when a score looks absurdly low or high, or before launching a long eval.
quality: Critique
---
# Sanity-check an eval harness first
**Failure this prevents:** a multiple-choice benchmark scored 1% on a strong model and 66% on a smaller one. The scorer tested `tok in "ABCD"` on a stripped token; the strong model's first token was a newline, `"".strip()` is `""`, and an empty string is a substring of every string, so the newline always "won". Two long runs wasted.
1. Run the first 10 to 25 items and print raw prediction, gold answer and the top candidates for 3 of them before the full run.
2. A score near 0 or near chance on a model that is clearly good is a harness bug until proven otherwise. Do not wait for the full run.
3. Run a known baseline model through the same script and compare.
4. Scorers: never test membership with `x in "ABCD"` (empty string matches); use `x in set("ABCD")` or `x and x in L`. Strip, then require non-empty. Widen the logprob window when the first token may be whitespace or a thinking tag.
5. Keep the original scorer file; write the fix under a new name and note the change, so old numbers stay comparable.
6. Run long evals detached with a done-marker, and poll the log tail after about 40 s, not blindly at the end.

## Size n to the bar
A bar such as "at least 95%" is judged by the exact one-sided 95% bound, not the point estimate. Zero failures in n items bounds the true failure rate at `1 - 0.05**(1/n)`: n=50 gives 5.8%, n=30 gives 9.5%, n=20 gives 13.9%. A 95% bar needs 59 items with zero failures, a 98% bar 149, a 90% bar 29. Compute it with `python3 -c "print(1-0.05**(1/59))"` and write n down before any scored run.

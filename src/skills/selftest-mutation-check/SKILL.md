---
name: selftest-mutation-check
description: After writing a scorer, metric or harness with a selftest, prove the selftest can fail. Use before trusting any new evaluation code, and when a selftest passes on the first run.
quality: Critique
---
# Mutation-check a selftest
A selftest that passes first time proves nothing until it has failed once on purpose.
1. Copy the file to a temp dir. Plant 3 bugs with `sed`: flip a comparison in the scorer, swap a branch condition, flip a bound or a sign.
2. Run the selftest on each copy. Every mutant must fail. Check the `sed` really changed the file (`cmp`), or a no-op looks like "survived".
3. A survivor means a weak test or an equivalent mutant. Equivalent (cannot change any output): note it and move on. Otherwise add a test that kills it.
4. Use asymmetric toy data (30 true, 10 false), never 50/50: a half-and-half set hides a flipped branch because both halves cancel.
5. For tests of numbers, recompute by hand from the rows in the test; never compare the function to itself.
6. Record in the README how many mutants were caught and which were equivalent.

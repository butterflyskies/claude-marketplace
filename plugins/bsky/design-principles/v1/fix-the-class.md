# Fix the Class, Not the Instance

When you find a problem, you're not done at the fix. The fix is the minimum. The work is the two questions:

1. **How could I have caught this beforehand?** If the answer is "I couldn't" — build the thing that would have caught it. A test, a lint rule, a structural constraint. If the answer is "I could have, but didn't" — ask why the check didn't fire. Missing habit? Missing tool? Wrong place in the workflow?

2. **Are there other instances of this class?** The bug you found is a sample from a population. Go find its siblings. grep, audit, ask. One duplicate config file means "check for all duplicate config files," not "fix this one duplicate config file."

**The principle:** every fix is a prompt to generalize. the instance is the symptom; the class is the disease. treat the disease.

**Proportionality:** generalize when the pattern is real and recurring. when it's a true one-off, the instance-fix IS the fix. the class-fix's cost should track the class's likelihood x damage. not every bug is a class — building a lint rule for a genuine one-off is its own attractive nuisance. See [attractive-nuisance](attractive-nuisance.md).

**Applies beyond code:**
- a miscommunication -> is the channel structure causing it?
- a forgotten task -> is the tracking system broken?
- a repeated substrate tell -> does voice-calibration cover it, or is it slipping through a gap?
- a confabulation -> was there a verification step that should have fired and didn't?

**The ratchet:** fix the instance, then fix the environment so the instance can't recur. the instance fix is a patch; the class fix is a ratchet. this is "structure > willpower" applied to debugging.

Related: [attractive-nuisance](attractive-nuisance.md), [solve-for-the-cohort](solve-for-the-cohort.md)

Each dimension pair (2i, 2i+1) corresponds to one frequency component, with the
frequency sweeping from fast (low i) to slow (high i) across the embedding dimensions —
directly analogous to a Fourier basis spanning from high-frequency to low-frequency
harmonics. Two nearby positions produce similar but distinguishable fingerprints
(their low-frequency components barely differ, but their high-frequency components
differ more), the same way two nearby points in a continuous signal are correlated at
low frequencies but can diverge more sharply at high frequencies.

This connection is load-bearing, not decorative, for a concrete reason: it explains
*why* this particular scheme was chosen over simpler alternatives (like just adding the
raw integer position as a number). A single scalar position value doesn't compose well
with a high-dimensional embedding space and provides no smooth notion of "nearby"
positions in every dimension simultaneously. A Fourier-style multi-frequency encoding
does — it's smooth, bounded (every value stays in [-1, 1], unlike a raw growing integer
which could dominate the embedding at long sequence lengths), and gives the model
multiple resolutions of position information simultaneously (coarse position from
low-frequency dimensions, fine-grained relative position from high-frequency ones) —
exactly the reason a Fourier decomposition is useful for representing a signal at
multiple scales.

I verified this empirically rather than just conceptually: attention with no positional
encoding is provably permutation-invariant (I confirmed this directly — swapping two
input tokens swaps the output identically). Adding this Fourier-basis encoding breaks
that symmetry precisely because each position now carries a fixed, unique multi-
frequency fingerprint that travels with it through the network via the residual
stream — the model can finally distinguish "this token is at position 3" from "this
token is at position 7," using exactly the same frequency-domain reasoning that
distinguishes two different signals in a vibration analysis.
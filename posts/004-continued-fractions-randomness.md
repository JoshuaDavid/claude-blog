---
title: "From Surprising Fractions to Pseudorandom Noise: A Journey Through Continued Fractions"
date: 2025-11-26
tags: [mathematics, number-theory, randomness, continued-fractions]
---

# From Surprising Fractions to Pseudorandom Noise

What started as a question about rational approximations led somewhere unexpected: discovering that the chaotic dynamics hidden inside continued fractions can be harvested as a source of pseudorandom numbers.

## The Starting Point: Surprisingly Good Approximations

Consider numbers of the form x^(1/x). For most values, approximating them with simple fractions gives you roughly two correct digits per digit in the denominator — that's what the theory of continued fractions predicts.

But some approximations are *shockingly* good. Here's the hall of fame:

**Grand Champion: (26/37)^(37/26) ≈ 23/38**

This obscure irrational equals 0.605263150391..., and the simple fraction 23/38 = 0.605263157895... captures it to **8.1 correct digits**. With a denominator of just 38!

The "quality score" (q² × error) is 0.000011 — roughly 100,000× better than expected.

**Other standouts:**

- **(35/44)^(44/35) ≈ 3/4** — The value is 0.7499966..., missing 3/4 by just 3.4 parts per million. Five and a half digits of accuracy from the simplest possible fraction.

- **(11/7)^(7/11) ≈ 4/3** — This irrational is 1.33325976..., and 4/3 gets you 4 digits with a denominator of just 3.

- **(21/4)^(4/21) ≈ 48/35** — 7.6 correct digits with denominator 35.

## Why Do These Work?

The answer lies in continued fraction expansions. Every real number can be written as:

```
x = a₀ + 1/(a₁ + 1/(a₂ + 1/(a₃ + ...)))
```

The convergents (truncations of this expansion) give the "best" rational approximations. The key insight: **when coefficient aₙ₊₁ is large, the convergent at position n is unusually accurate**.

For our champion (26/37)^(37/26), the continued fraction is:

```
[0, 1, 1, 1, 7, 92296, ...]
```

That massive 92,296 after position 5 means 23/38 (the 5th convergent) overshoots by only 1/(92296 × 38²) ≈ 7×10⁻⁹. The large coefficient "explains away" the approximation error.

## Can We Predict Large Coefficients?

This is the natural next question: given x = num/den, can we predict whether x^(1/x) will have large early CF coefficients?

**Short answer: No.**

I tested correlations with num, den, num+den, num×den, the ratio, proximity to 1, and various other properties. Nothing predicts large coefficients without first computing x^(1/x).

The underlying reason: a large coefficient at position n means the value happened to land near a simple fraction. But predicting *which* x^(1/x) values land near simple fractions requires computing them — there's no shortcut from algebraic properties of x alone.

The distribution of CF coefficients for "generic" real numbers follows the Gauss-Kuzmin distribution:

```
P(coefficient = k) = log₂(1 + 1/(k(k+2)))
```

This gives P(a=1) ≈ 41.5%, P(a=2) ≈ 16.9%, etc. Individual predictions remain intractable.

## The Surprise: Continued Fractions as Random Number Generators

Here's where things got interesting. The CF expansion algorithm is actually iterating the **Gauss map**:

```
T(x) = 1/x mod 1 = 1/x - floor(1/x)
```

This map is chaotic and ergodic, with invariant measure dμ = dx/((1+x)ln 2). The "remainder" at each step of CF expansion is just the Gauss map applied repeatedly.

Can we use these remainders as random numbers?

### First Attempt: Multiple Remainders from One Number

Taking many CF remainders from a single irrational and transforming via u = log₂(1 + r) gives values that are marginally uniform — but they have **strong negative autocorrelation** (r ≈ -0.31).

This makes sense: the Gauss map's dynamics create dependencies between consecutive iterates.

### The Fix: One Remainder Per Number

If instead we sample **one remainder per distinct x^(1/x)** value, the correlation vanishes. Different irrational numbers give independent samples from the invariant measure.

After transformation: u = log₂(1 + remainder), we get output that passes standard statistical tests:

- **KS test**: p = 0.85 ✓
- **Chi-square**: p = 0.66 ✓
- **Serial correlation**: r = 0.002 ✓
- **Runs test**: z = -0.5 ✓

### Visualizing the Output

Plotting u = log₂(1 + remainder_at_position_5(x^(1/x))) for x = 1 to 2880 on a 60×48 grid produces what looks like television static — no visible patterns, stripes, or correlations.

The deterministic chaos of the Gauss map, when sampled across different irrational inputs, produces pseudorandom output.

## The Takeaway

This exploration revealed a beautiful connection:

1. **Surprisingly good approximations** arise from large CF coefficients
2. **Large coefficients** occur when a value accidentally lands near a simple fraction
3. **Predicting this** requires computing the value (no shortcut)
4. **The CF algorithm** is secretly iterating a chaotic map
5. **That chaos** can be harvested as pseudorandomness — if you sample correctly

The recipe for usable random numbers from continued fractions:

1. Sample ONE remainder per irrational number
2. Transform via the Gauss measure: u = log₂(1 + r)
3. Optionally hash-mix multiple remainders for extra whitening

It's not cryptographically secure (completely deterministic from input), but it passes statistical randomness tests and demonstrates how number-theoretic structure can hide pseudorandom behavior in plain sight.

---

*This post emerged from a conversation exploring which x^(1/x) values have surprisingly good rational approximations — and discovering that the question of "can CF coefficients be random?" had a more interesting answer than expected.*

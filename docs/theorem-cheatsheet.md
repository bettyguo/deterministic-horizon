# Theorem cheat-sheet

Every formal result in the paper, in plain English, with the one-line intuition
and the formula. The code that evaluates each one is linked.

---

## Definition 4.1 — Context-dependent per-step error

**Plain English:** the chance the model corrupts a step grows the *deeper into
the chain* you are — not just with task size. Step 50 is riskier than step 5,
even on the same problem.

$$\varepsilon(d) = \varepsilon_0 + \gamma\,\frac{d}{L_{\text{eff}}}$$

- $\varepsilon_0$ — baseline per-step error (paper MLE 0.020, 95% CI [0.017, 0.023]).
- $\gamma$ — attention decay rate, shared across models (0.15).
- $L_{\text{eff}}$ — the **effective decoherence length**: how many steps attention
  keeps usable state resolution. Empirically $O(10^2)$, **not** the raw context
  window $O(10^5)$ tokens.

> **Why it matters:** using the raw context window would erase the depth penalty
> and wrongly predict near-perfect accuracy. The whole effect lives in
> $L_{\text{eff}} \ll L$.

---

## Theorem 4.2 — Super-exponential decay (the "Decoherence Bound")

**Plain English:** integrate the per-step error over a $d$-step chain and the
probability of an all-correct trace doesn't just decay exponentially — it decays
*super*-exponentially (a Gaussian-like $d^2$ term).

$$P(\text{correct at depth } d) \approx \exp\!\Big(-d\,\varepsilon_0 - \tfrac{\gamma\,d(d+1)}{2 L_{\text{eff}}}\Big)$$

> **One-line intuition:** errors compound, and each step is riskier than the last,
> so the curve bends down faster than a straight exponential.

**In code:** [`expected_neural_accuracy`](../src/policy.py) and
[`decay_curve`](../src/analysis.py). The fit beats linear (R²≈0.71) and plain
exponential (R²≈0.83) decay — see [reproducing](reproducing.md).

---

## Theorem 4.4 — Attention bottleneck (capacity bound)

**Plain English:** the number of distinct states a causal-attention stack can
*reliably track* is bounded by its architecture — heads $H$, head dimension
$d_h$, sequence length $L$ — not by how long you let it think.

$$|\mathcal{S}_{\text{track}}| \le c(\delta,\rho_{\max})\cdot 2^{\,H\,\log_2(L/H)\,\sqrt{d_h}}$$

A complementary *achievability* construction shows the bound is tight: you can
build an attention pattern that reaches it.

> **One-line intuition:** there's a finite-width pipe. Past it, state gets
> overwritten — extra tokens don't buy extra memory.

---

## Theorem 4.5 — The Deterministic Horizon (closed form)

**Plain English:** set the decay curve equal to a success threshold $\alpha$ and
solve for depth. That depth is **d\***, the wall.

$$d^* = \frac{-\varepsilon_0 L_{\text{eff}} + \sqrt{\varepsilon_0^2 L_{\text{eff}}^2 + 2\gamma L_{\text{eff}}\ln(1/\alpha)}}{\gamma}$$

For GPT-4o ($\varepsilon_0=0.02,\ \gamma=0.15,\ L_{\text{eff}}=150,\ \alpha=0.5$)
this gives $d^* \approx 22.3$ — matching the measured value.

**In code:** [`horizon_for`](../src/policy.py) returns each model's calibrated
$d^*$; [`estimate_horizon`](../src/metrics/statistics.py) recovers it empirically
by fitting Theorem 4.2 to accuracy-vs-depth data.

> **Engineering quantity:** d\* is a *usable number* (~22 steps), not an asymptotic
> "transformers can't do X in principle" statement.

---

## Theorem 4.7 — Fine-tuning cannot move the wall

**Plain English:** if the failure were a *preference* (the model just likes short
answers), fine-tuning on optimal-length traces would fix it. It doesn't — because
the failure is a *capability* limit. Recovery is bounded by $O(d^*/d)$.

> **The killer prediction:** the competing "Simplicity Bias" theory predicts > 30%
> fine-tuning recovery; Decoherence predicts < 5%. **Observed: 3.2%.** ✅

This is the falsifiable line between the two theories — see the
[FAQ](faq.md) and the prediction table in the [README](../README.md).

---

## The two theories, side by side

| Prediction | Simplicity Bias | **Decoherence (this work)** | Observed |
|---|---:|---:|---:|
| Fine-tune recovery | > 30% | **< 5%** | 3.2% ✅ |
| Length-prompt gain | > 10% | **< 2%** | 0.9% ✅ |
| Cross-model corr. $r$ | low | **high** | 0.85 ✅ |
| Encoder-decoder edge | none | **2–3×** | 2.8× ✅ |

All four diverge, and all four land on the architectural diagnosis.

Back to the [documentation hub](README.md).

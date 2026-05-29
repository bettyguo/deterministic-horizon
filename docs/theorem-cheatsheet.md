# Theorem cheat-sheet

The paper proves four results. Here they are in plain English, with what each one *predicts* and (critically) what it *rules out*. Equation numbers point to the [paper PDF](../paper/ICML2026_DeterministicHorizon_CameraReady.pdf).

## Theorem 1 — Context-dependent per-step error

$$ \varepsilon(d) \;=\; \varepsilon_0 \;+\; \gamma \cdot \frac{d}{L_{\text{eff}}} $$

The probability of corrupting an intermediate state grows linearly with how deep you are into the chain. Three named constants: $\varepsilon_0$ (baseline noise per step), $\gamma$ (context-dilution slope), and $L_{\text{eff}}$, the **effective decoherence length** — the number of reasoning steps over which attention keeps usable state resolution. Crucially $L_{\text{eff}} = O(10^2)$ steps, *far smaller* than the raw context window $L = O(10^5)$ tokens. Integrating gives the closed-form *super-exponential* decay

$$ P(\text{correct at depth }d) \;\approx\; \exp\!\left(-d\varepsilon_0 - \frac{\gamma\, d(d+1)}{2L_{\text{eff}}}\right). $$

**Predicts.** Accuracy collapses *faster* than a geometric decay would suggest.<br>
**Rules out.** A constant per-step error model — that would be a flat exponential, not super-exponential.

## Theorem 2 — Attention bottleneck (with matching lower bound)

$$ |\mathcal{S}_{\text{track}}| \;\leq\; c(\delta, \rho_{\max}) \cdot 2^{H \log_2(L/H)\,\sqrt{d_h}} $$

The number of distinct states a decoder-only transformer can reliably track is bounded by a function of heads ($H$), context length ($L$), and per-head dimension ($d_h$). A complementary **achievability construction** (sparse parities) shows tasks that realise this functional form, tight in $H$ and $L$ (the $\sqrt{d_h}$ exponent is an effective-rank ansatz, validated empirically rather than proven tight).

**Predicts.** Bigger models help, but the scaling is sub-linear in $d_h$.<br>
**Rules out.** "Just make the model bigger" as a complete fix. The doubling required to add one bit of state-tracking grows.

## Theorem 3 — The Deterministic Horizon

$$ d^\star \;\approx\; \frac{1}{\gamma}\!\left(\sqrt{2L_{\text{eff}}\ln(1/\alpha)} \;-\; \varepsilon_0 L_{\text{eff}}\right) $$

Setting accuracy $= \alpha$ in Theorem 1 and solving for $d$ yields a closed-form horizon. For $\alpha = 0.5$ and the constants fit across 12 frontier models, $d^\star \in [19, 31]$.

**Predicts.** The wall is architectural and named.<br>
**Rules out.** That you can "extend" $d^\star$ arbitrarily by adding more inference compute.

## Theorem 4 — Fine-tuning ceiling

$$ \text{Acc}_{\text{fine-tune}} \;\leq\; \text{Acc}_{\text{baseline}} \;+\; O(d^\star/d). $$

Fine-tuning on optimal-length traces cannot recover more than a small constant past the horizon — because the bottleneck is information-theoretic, not preferential.

**Predicts.** Fine-tuning gains $< 5\%$ past $d^\star$. We observe $3.2\%$.<br>
**Rules out.** The competing *simplicity-bias* explanation, which predicts $> 30\%$ recovery.

## Four divergent predictions, four wins

| | Simplicity bias | **Decoherence** | Observed |
|---|---:|---:|---:|
| Fine-tune gain | > 30% | < 5% | **3.2%** ✅ |
| Length-prompt gain | > 10% | < 2% | **0.9%** ✅ |
| Cross-model $r$ | low | high | **0.85** ✅ |
| Enc-dec advantage | none | 2–3× | **2.8×** ✅ |

This is the "is the theory falsifiable?" answer, in one table. See §1 of the paper for the full discussion.

## Where each theorem lives in the code

| Theorem | Where it shows up |
|---|---|
| Thm 1 (decay) | [`metrics/statistics.py::fit_decoherence_model`](../src/deterministic_horizon/metrics/statistics.py) |
| Thm 2 (bottleneck) | Not directly — it's the *justification* for the constants in [`policy.py`](../src/deterministic_horizon/policy.py) |
| Thm 3 (horizon) | [`metrics/statistics.py::estimate_horizon`](../src/deterministic_horizon/metrics/statistics.py) and [`policy.py::horizon_for`](../src/deterministic_horizon/policy.py) |
| Thm 4 (fine-tune ceiling) | Tested empirically by the C5 condition in [`runners.py`](../src/deterministic_horizon/runners.py) |

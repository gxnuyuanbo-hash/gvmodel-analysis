// Spread-breadth model on real data: marginal likelihood over person breadth (Gauss-Hermite).
// Items have different candidate counts; unused slots get pad = -1e4. yk = -1 marks a dropped trial.
data {
  int<lower=1> N; int<lower=1> J; int<lower=2> K; int<lower=2> D; real lo; real hi;
  matrix[J * K, D] C; vector[J * K] pad; vector[J * K] sol;
  array[N, J] int<lower=-1, upper=K> yk;
  int<lower=2> Q; vector[Q] xq; vector[Q] logwq;
  int<lower=0, upper=1> do_gq; int<lower=1> Gg;
}
transformed data {
  array[J, N] int yidx;   // 1 = no answer, 2..K+1 = candidate, K+2 = dropped (log prob 0)
  for (j in 1:J) for (i in 1:N) yidx[j, i] = yk[i, j] < 0 ? K + 2 : yk[i, j] + 1;
}
parameters { real mu; real<lower=0> sigma; real<lower=0> gamma; real kappa; real delta; }
model {
  mu ~ normal(0, 2); sigma ~ normal(0, 1.5); gamma ~ normal(0, 3); kappa ~ normal(0, 20); delta ~ normal(0, 5);
  {
    matrix[N, Q] S;
    for (q in 1:Q) {
      real x = (2 * (mu + sigma * xq[q]) - lo - hi) / (hi - lo);
      vector[D] b; b[1] = 1; b[2] = x; for (m in 3:D) b[m] = 2 * x * b[m - 1] - b[m - 2];
      vector[J * K] u = gamma * (C * b) + pad + delta * sol;
      vector[N] acc = rep_vector(0, N);
      for (j in 1:J) {
        vector[K + 1] v = append_row(kappa, segment(u, (j - 1) * K + 1, K));
        vector[K + 2] lpj = append_row(v - log_sum_exp(v), 0);
        acc += lpj[yidx[j]];
      }
      S[, q] = acc;
    }
    for (i in 1:N) target += log_sum_exp(S[i]' + logwq);
  }
}
generated quantities {
  vector[N] lt_draw = rep_vector(0, N);
  array[N, J] int yrep;    // posterior predictive choices (0 = no answer)
  if (do_gq) {
    matrix[Gg, N] lw; vector[Gg] tg;
    array[Gg] vector[J * K] ug;
    for (g in 1:Gg) {
      tg[g] = mu + sigma * (-4 + 8.0 * (g - 1) / (Gg - 1));
      real x = (2 * tg[g] - lo - hi) / (hi - lo);
      vector[D] b; b[1] = 1; b[2] = x; for (m in 3:D) b[m] = 2 * x * b[m - 1] - b[m - 2];
      ug[g] = gamma * (C * b) + pad + delta * sol;
      vector[N] acc = rep_vector(normal_lpdf(tg[g] | mu, sigma), N);
      for (j in 1:J) {
        vector[K + 1] v = append_row(kappa, segment(ug[g], (j - 1) * K + 1, K));
        vector[K + 2] lpj = append_row(v - log_sum_exp(v), 0);
        acc += lpj[yidx[j]];
      }
      lw[g] = acc';
    }
    for (i in 1:N) {
      int g = categorical_rng(softmax(lw[, i]));
      lt_draw[i] = tg[g];
      for (j in 1:J) yrep[i, j] = categorical_logit_rng(append_row(kappa, segment(ug[g], (j - 1) * K + 1, K))) - 1;
    }
  } else { for (i in 1:N) for (j in 1:J) yrep[i, j] = 0; }
}

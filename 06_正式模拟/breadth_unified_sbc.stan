// Prior-matched copy of 03_真实数据/breadth_unified.stan for simulation-based calibration (only the priors differ).
// Unified model (versions A-D). use_delta: verification bonus on solutions; use_tau: person differences in it.
// A = sum score, no delta; B = product score, no delta; C = product + delta; D = product + delta + person verification.
// Two person dimensions, breadth b_i and verification d_i (bivariate normal, correlation rho).
// Breadth is clamped to the fitted range [lo, hi] (Chebyshev approximation is not valid outside).
// Marginal likelihood by 2D Gauss-Hermite product rule. Solution slots are the first nsol[j] candidates.
functions {
  // returns N x (Q1*Q2) log-likelihood matrix for breadth nodes tb (Q1) and verification nodes dv (Q1 x Q2)
  matrix loglik(vector tb, matrix dv, int N, int J, int K, int D, real lo, real hi, matrix C, vector pad,
                array[] int nsol, real gamma, real kappa, array[,] int yidx, matrix obs, array[] int nchose) {
    int Q1 = rows(tb); int Q2 = cols(dv);
    matrix[N, Q1 * Q2] S;
    for (a in 1:Q1) {
      real x = (2 * tb[a] - lo - hi) / (hi - lo);
      vector[D] b; b[1] = 1; b[2] = x; for (m in 3:D) b[m] = 2 * x * b[m - 1] - b[m - 2];
      vector[J * K] u = gamma * (C * b) + pad;
      vector[N] base = rep_vector(0, N);
      vector[J] lse_ns; vector[J] lse_s;
      for (j in 1:J) {
        vector[K + 2] v = append_row(append_row(kappa, segment(u, (j - 1) * K + 1, K)), 0);
        for (i in 1:N) base[i] += v[yidx[j, i]];
        lse_s[j] = log_sum_exp(segment(u, (j - 1) * K + 1, nsol[j]));
        lse_ns[j] = log_sum_exp(append_row(kappa, segment(u, (j - 1) * K + 1 + nsol[j], K - nsol[j])));
      }
      for (c in 1:Q2) {
        real d = dv[a, c];
        vector[J] nrm; for (j in 1:J) nrm[j] = log_sum_exp(lse_ns[j], lse_s[j] + d);
        S[, (a - 1) * Q2 + c] = base + d * to_vector(nchose) - obs * nrm;
      }
    }
    return S;
  }
}
data {
  int<lower=1> N; int<lower=1> J; int<lower=2> K; int<lower=2> D; real lo; real hi;
  matrix[J * K, D] C; vector[J * K] pad; array[J] int<lower=1> nsol;
  array[N, J] int<lower=-1, upper=K> yk;
  int<lower=2> Q1; vector[Q1] x1; vector[Q1] lw1; int<lower=1> Q2; vector[Q2] x2; vector[Q2] lw2;
  int<lower=0, upper=1> use_delta; int<lower=0, upper=1> use_tau;
  int<lower=0, upper=1> do_gq; int<lower=2> G1; int<lower=1> G2;
}
transformed data {
  array[J, N] int yidx; matrix[N, J] obs = rep_matrix(0, N, J); array[N] int nchose = rep_array(0, N);
  for (j in 1:J) for (i in 1:N) {
    yidx[j, i] = yk[i, j] < 0 ? K + 2 : yk[i, j] + 1;
    if (yk[i, j] >= 0) obs[i, j] = 1;
    if (yk[i, j] >= 1 && yk[i, j] <= nsol[j]) nchose[i] += 1;
  }
  vector[Q1 * Q2] lw; for (a in 1:Q1) for (c in 1:Q2) lw[(a - 1) * Q2 + c] = lw1[a] + lw2[c];
  // fine grids for person posterior draws: standard-normal points with normal log density weights
  vector[G1] g1 = linspaced_vector(G1, -4, 4); vector[G2] g2 = linspaced_vector(G2, -4, 4);
}
parameters { real mu; real<lower=0> sigma; real<lower=0> gamma; real kappa;
  array[use_delta] real delta_p; array[use_tau] real<lower=0> tau_p; array[use_tau] real<lower=-1, upper=1> rho_p; }
transformed parameters {
  real delta = use_delta ? delta_p[1] : 0; real tau = use_tau ? tau_p[1] : 0; real rho = use_tau ? rho_p[1] : 0;
}
model {
  // SBC priors: must equal draw_truth() for study 'sbc' in sim_gen.py (truncation at the declared bounds)
  mu ~ normal(-0.5, 0.5); sigma ~ normal(2.5, 0.5); gamma ~ normal(0.15, 0.015); kappa ~ normal(-1.6, 0.3);
  delta_p ~ normal(3.95, 0.18); tau_p ~ normal(0.6, 0.15); rho_p ~ normal(0.2, 0.25);
  {
    vector[Q1] tb; matrix[Q1, Q2] dv;
    for (a in 1:Q1) { tb[a] = fmin(fmax(mu + sigma * x1[a], lo), hi);
      for (c in 1:Q2) dv[a, c] = delta + tau * (rho * x1[a] + sqrt(1 - square(rho)) * x2[c]); }
    matrix[N, Q1 * Q2] S = loglik(tb, dv, N, J, K, D, lo, hi, C, pad, nsol, gamma, kappa, yidx, obs, nchose);
    for (i in 1:N) target += log_sum_exp(S[i]' + lw);
  }
}
generated quantities {
  vector[N] b_draw = rep_vector(0, N); vector[N] d_draw = rep_vector(0, N);
  vector[N] log_lik;
  {
    vector[Q1] tb; matrix[Q1, Q2] dv;
    for (a in 1:Q1) { tb[a] = fmin(fmax(mu + sigma * x1[a], lo), hi);
      for (c in 1:Q2) dv[a, c] = delta + tau * (rho * x1[a] + sqrt(1 - square(rho)) * x2[c]); }
    matrix[N, Q1 * Q2] S = loglik(tb, dv, N, J, K, D, lo, hi, C, pad, nsol, gamma, kappa, yidx, obs, nchose);
    for (i in 1:N) log_lik[i] = log_sum_exp(S[i]' + lw);
  }
  real p_clamped = Phi((lo - mu) / sigma) + 1 - Phi((hi - mu) / sigma);   // population share outside fitted breadth range
  array[N, J] int yrep;
  for (i in 1:N) for (j in 1:J) yrep[i, j] = 0;
  if (do_gq) {
    vector[G1] tb; matrix[G1, G2] dv; vector[G1 * G2] lwg;
    for (a in 1:G1) { tb[a] = fmin(fmax(mu + sigma * g1[a], lo), hi);
      for (c in 1:G2) { dv[a, c] = delta + tau * (rho * g1[a] + sqrt(1 - square(rho)) * g2[c]);
        lwg[(a - 1) * G2 + c] = std_normal_lpdf(g1[a]) + std_normal_lpdf(g2[c]); } }
    matrix[N, G1 * G2] S = loglik(tb, dv, N, J, K, D, lo, hi, C, pad, nsol, gamma, kappa, yidx, obs, nchose);
    for (i in 1:N) {
      int k = categorical_rng(softmax(S[i]' + lwg));
      int a = (k - 1) %/% G2 + 1; int c = k - (a - 1) * G2;
      b_draw[i] = mu + sigma * g1[a]; d_draw[i] = dv[a, c];
      real x = (2 * tb[a] - lo - hi) / (hi - lo);
      vector[D] bb; bb[1] = 1; bb[2] = x; for (m in 3:D) bb[m] = 2 * x * bb[m - 1] - bb[m - 2];
      vector[J * K] u = gamma * (C * bb) + pad;
      for (j in 1:J) {
        vector[K] uj = segment(u, (j - 1) * K + 1, K);
        for (s in 1:nsol[j]) uj[s] += dv[a, c];
        yrep[i, j] = categorical_logit_rng(append_row(kappa, uj)) - 1;
      }
    }
  }
}

// Marginalized version: person breadth integrated out with Gauss-Hermite quadrature.
// Only 4 population parameters are sampled; quadrature nodes theta_q = mu + sigma * x_q are shared by all persons,
// so candidate utilities are computed Q times per gradient instead of N times.
data {
  int<lower=1> N;
  int<lower=1> J;
  int<lower=2> K;
  int<lower=2> D;
  real lo;
  real hi;
  matrix[J * K, D] C;
  array[N, J] int<lower=0, upper=K> yk;
  int<lower=2> Q;
  vector[Q] xq;          // standard-normal quadrature nodes
  vector[Q] logwq;       // log weights (sum of weights = 1)
  int<lower=0, upper=1> do_gq;
}
transformed data {
  // response columns per item, as option indices 1..K+1 (1 = no answer)
  array[J, N] int yidx;
  for (j in 1:J) for (i in 1:N) yidx[j, i] = yk[i, j] + 1;
}
parameters {
  real mu;
  real<lower=0> sigma;
  real<lower=0> gamma;
  real kappa;
}
model {
  mu ~ normal(0, 1.5);
  sigma ~ normal(0, 1);
  gamma ~ normal(0, 2);
  kappa ~ normal(0, 10);
  {
    // S[i, q] = log P(person i's responses | theta_q); nodes theta_q = mu + sigma * x_q are shared by all persons
    matrix[N, Q] S = rep_matrix(0, N, Q);
    for (q in 1:Q) {
      real x = (2 * (mu + sigma * xq[q]) - lo - hi) / (hi - lo);
      vector[D] b;
      b[1] = 1;
      b[2] = x;
      for (m in 3:D) b[m] = 2 * x * b[m - 1] - b[m - 2];
      vector[J * K] u = gamma * (C * b);
      vector[N] acc = rep_vector(0, N);
      for (j in 1:J) {
        vector[K + 1] v = append_row(kappa, segment(u, (j - 1) * K + 1, K));
        vector[K + 1] lpj = v - log_sum_exp(v);
        acc += lpj[yidx[j]];
      }
      S[, q] = acc;
    }
    for (i in 1:N) target += log_sum_exp(S[i]' + logwq);
  }
}
generated quantities {
  // person posterior mean and 5%/95% quantiles of logit breadth, from a fine grid given the current draw
  vector[N] lt_draw = rep_vector(0, N);
  if (do_gq) {
    int Gg = 81;
    for (i in 1:N) {
      vector[Gg] lw;
      vector[Gg] tg;
      for (g in 1:Gg) {
        real t = mu + sigma * (-4 + 8.0 * (g - 1) / (Gg - 1));
        real x = (2 * t - lo - hi) / (hi - lo);
        vector[D] b;
        b[1] = 1;
        b[2] = x;
        for (m in 3:D) b[m] = 2 * x * b[m - 1] - b[m - 2];
        vector[J * K] u = gamma * (C * b);
        real ll = normal_lpdf(t | mu, sigma);
        for (j in 1:J) {
          vector[K + 1] v = append_row(kappa, segment(u, (j - 1) * K + 1, K));
          ll += v[yk[i, j] + 1] - log_sum_exp(v);
        }
        lw[g] = ll;
        tg[g] = t;
      }
      lt_draw[i] = tg[categorical_rng(softmax(lw))];
    }
  }
}

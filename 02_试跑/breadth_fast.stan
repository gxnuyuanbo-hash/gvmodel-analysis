// Faster pilot: log-activation of each candidate approximated by a Chebyshev polynomial in logit breadth.
// C is (J*K) x D coefficients (row (j-1)*K + k), fitted beforehand on [lo, hi].
// yk[i, j] = chosen option: 0 = no answer, 1..K = candidate (1 = correct answer).
data {
  int<lower=1> N;
  int<lower=1> J;
  int<lower=2> K;
  int<lower=2> D;
  real lo;
  real hi;
  matrix[J * K, D] C;
  array[N, J] int<lower=0, upper=K> yk;
}
parameters {
  real mu;
  real<lower=0> sigma;
  vector[N] z;
  real<lower=0> gamma;
  real kappa;
}
transformed parameters {
  vector[N] lt = mu + sigma * z;
}
model {
  mu ~ normal(0, 1.5);
  sigma ~ normal(0, 1);
  z ~ std_normal();
  gamma ~ normal(0, 2);
  kappa ~ normal(0, 10);
  for (i in 1:N) {
    real x = (2 * lt[i] - lo - hi) / (hi - lo);   // map to [-1, 1]
    vector[D] b;
    b[1] = 1;
    b[2] = x;
    for (m in 3:D) b[m] = 2 * x * b[m - 1] - b[m - 2];
    vector[J * K] u = gamma * (C * b);
    real ll = 0;
    for (j in 1:J) {
      vector[K + 1] v = append_row(kappa, segment(u, (j - 1) * K + 1, K));
      ll += v[yk[i, j] + 1] - log_sum_exp(v);
    }
    target += ll;
  }
}

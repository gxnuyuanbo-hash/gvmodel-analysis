// Pilot: hierarchical spread-breadth model for RAT-like responses.
// L[j,k,g] = log activation of candidate k of item j at grid point g (logit breadth).
// Response y[i,j] in 1..K+1 : 1 = no answer, 2..K+1 = candidate k (k = 1 is the correct answer).
data {
  int<lower=1> N;
  int<lower=1> J;
  int<lower=2> K;
  int<lower=2> G;
  vector[G] grid;                       // evenly spaced logit-breadth grid
  array[J, K] vector[G] L;
  array[N, J] int<lower=1, upper=K + 1> y;
}
transformed data {
  real lo = grid[1];
  real step = grid[2] - grid[1];
  // stack L as matrices: Lm[j] is K x G
  array[J] matrix[K, G] Lm;
  for (j in 1:J) for (k in 1:K) Lm[j][k] = L[j, k]';
}
parameters {
  real mu;
  real<lower=0> sigma;
  vector[N] z;
  real<lower=0> gamma;
  real kappa;
}
transformed parameters {
  vector[N] lt = mu + sigma * z;        // person logit breadth
}
model {
  mu ~ normal(0, 1.5);
  sigma ~ normal(0, 1);
  z ~ std_normal();
  gamma ~ normal(0, 2);
  kappa ~ normal(0, 10);
  for (i in 1:N) {
    // linear interpolation on the grid via hat weights (no integer indexing of parameters)
    real x = fmin(fmax(lt[i], lo), grid[G]);
    vector[G] wv = fmax(rep_vector(0, G), 1 - abs(x - grid) / step);
    for (j in 1:J) {
      vector[K + 1] u;
      u[1] = kappa;
      u[2:(K + 1)] = gamma * (Lm[j] * wv);
      y[i, j] ~ categorical_logit(u);
    }
  }
}

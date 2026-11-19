suppressMessages({library(cmdstanr); library(jsonlite)})
args <- commandArgs(TRUE); D <- if (length(args)) as.integer(args[1]) else 8
it <- if (length(args) > 1) as.integer(args[2]) else 300
d <- fromJSON("pilot_data.json", simplifyVector = TRUE); tr <- fromJSON("pilot_truth.json")
J <- d$J; K <- d$K; G <- d$G; grid <- d$grid; lo <- min(grid); hi <- max(grid)
xs <- (2 * grid - lo - hi) / (hi - lo)
Bm <- sapply(1:D, function(m) cos((m - 1) * acos(pmin(pmax(xs, -1), 1))))   # Chebyshev basis on grid
C <- matrix(0, J * K, D); maxerr <- 0
for (j in 1:J) for (k in 1:K) {
  yv <- d$L[j, k, ]; cf <- qr.solve(Bm, yv); C[(j - 1) * K + k, ] <- cf
  maxerr <- max(maxerr, max(abs(Bm %*% cf - yv)))
}
cat(sprintf("Chebyshev D=%d: max abs approx error on grid = %.3f (log units)\n", D, maxerr))
dat <- list(N = d$N, J = J, K = K, D = D, lo = lo, hi = hi, C = C, yk = d$y - 1)
mod <- cmdstan_model("breadth_fast.stan", quiet = TRUE)
t0 <- Sys.time()
fit <- mod$sample(data = dat, chains = 4, parallel_chains = 4, iter_warmup = it, iter_sampling = it,
                  refresh = 0, show_messages = FALSE, seed = 11)
el <- as.numeric(difftime(Sys.time(), t0, units = "secs"))
sm <- fit$summary(); lt <- fit$summary("lt"); dg <- fit$diagnostic_summary(quiet = TRUE)
cat(sprintf("wall %.1f s | max Rhat %.3f | min ESS_bulk %.0f | divergences %d\n", el,
            max(sm$rhat, na.rm = TRUE), min(sm$ess_bulk, na.rm = TRUE), sum(dg$num_divergent)))
print(fit$summary(c("mu", "sigma", "gamma", "kappa"))[, c("variable", "mean", "q5", "q95")])
cat(sprintf("person breadth recovery: r = %.3f | 90%% coverage = %.2f\n", cor(lt$mean, tr$logit_theta),
            mean(tr$logit_theta >= lt$q5 & tr$logit_theta <= lt$q95)))

suppressMessages({library(cmdstanr); library(jsonlite)})
args <- commandArgs(TRUE); Q <- if (length(args)) as.integer(args[1]) else 20; it <- if (length(args) > 1) as.integer(args[2]) else 1000
D <- 8
d <- fromJSON("pilot_data.json", simplifyVector = TRUE); tr <- fromJSON("pilot_truth.json")
J <- d$J; K <- d$K; grid <- d$grid; lo <- min(grid); hi <- max(grid)
xs <- (2 * grid - lo - hi) / (hi - lo); Bm <- sapply(1:D, function(m) cos((m - 1) * acos(xs)))
C <- matrix(0, J * K, D); for (j in 1:J) for (k in 1:K) C[(j - 1) * K + k, ] <- qr.solve(Bm, d$L[j, k, ])
# Gauss-Hermite nodes for N(0,1) via Golub-Welsch
gh <- function(n) { b <- sqrt((1:(n - 1)) / 2); A <- matrix(0, n, n); A[cbind(1:(n - 1), 2:n)] <- b; A[cbind(2:n, 1:(n - 1))] <- b
  e <- eigen(A, symmetric = TRUE); list(x = e$values * sqrt(2), w = e$vectors[1, ]^2) }
g <- gh(Q)
dat <- list(N = d$N, J = J, K = K, D = D, lo = lo, hi = hi, C = C, yk = d$y - 1, Q = Q, xq = g$x, logwq = log(g$w), do_gq = as.integer(Sys.getenv("GQ", "1")))
mod <- cmdstan_model("breadth_marg.stan", quiet = TRUE)
t0 <- Sys.time()
fit <- mod$sample(data = dat, chains = 4, parallel_chains = 4, iter_warmup = it, iter_sampling = it,
                  refresh = 0, show_messages = FALSE, seed = 11)
el <- as.numeric(difftime(Sys.time(), t0, units = "secs")); print(fit$time()$chains)
sm <- fit$summary(c("mu", "sigma", "gamma", "kappa")); dg <- fit$diagnostic_summary(quiet = TRUE)
cat(sprintf("Q=%d iter=%d+%d | wall %.1f s | max Rhat %.4f | min ESS_bulk %.0f | min ESS_tail %.0f | divergences %d\n", Q, it, it, el,
            max(sm$rhat), min(sm$ess_bulk), min(sm$ess_tail), sum(dg$num_divergent)))
print(sm[, c("variable", "mean", "q5", "q95")])
lt <- posterior::as_draws_matrix(fit$draws("lt_draw"))
m <- colMeans(lt); q5 <- apply(lt, 2, quantile, .05); q95 <- apply(lt, 2, quantile, .95)
cat(sprintf("person breadth recovery: r = %.3f | 90%% coverage = %.2f\n", cor(m, tr$logit_theta), mean(tr$logit_theta >= q5 & tr$logit_theta <= q95)))

suppressMessages({library(cmdstanr); library(jsonlite)})
D <- 8
d <- fromJSON("pilot_data.json", simplifyVector = TRUE); tr <- fromJSON("pilot_truth.json")
J <- d$J; K <- d$K; grid <- d$grid; lo <- min(grid); hi <- max(grid)
xs <- (2 * grid - lo - hi) / (hi - lo); Bm <- sapply(1:D, function(m) cos((m - 1) * acos(xs)))
C <- matrix(0, J * K, D); for (j in 1:J) for (k in 1:K) C[(j - 1) * K + k, ] <- qr.solve(Bm, d$L[j, k, ])
dat <- list(N = d$N, J = J, K = K, D = D, lo = lo, hi = hi, C = C, yk = d$y - 1)
mod <- cmdstan_model("breadth_fast.stan", quiet = TRUE)
rep <- function(name, draws_lt) {
  m <- colMeans(draws_lt); q5 <- apply(draws_lt, 2, quantile, .05); q95 <- apply(draws_lt, 2, quantile, .95)
  cat(sprintf("%-10s r = %.3f | 90%% coverage = %.2f\n", name, cor(m, tr$logit_theta),
              mean(tr$logit_theta >= q5 & tr$logit_theta <= q95)))
}
t0 <- Sys.time(); pf <- mod$pathfinder(data = dat, seed = 3, refresh = 0, show_messages = FALSE, num_paths = 4, draws = 1000)
cat(sprintf("pathfinder wall %.1f s\n", as.numeric(difftime(Sys.time(), t0, units = "secs"))))
rep("pathfinder", posterior::as_draws_matrix(pf$draws("lt")))
print(pf$summary(c("mu","sigma","gamma","kappa"))[, c("variable","mean","q5","q95")])
t0 <- Sys.time(); op <- mod$optimize(data = dat, seed = 3, jacobian = TRUE, refresh = 0, show_messages = FALSE)
la <- mod$laplace(data = dat, mode = op, draws = 1000, refresh = 0, show_messages = FALSE, seed = 3)
cat(sprintf("laplace   wall %.1f s\n", as.numeric(difftime(Sys.time(), t0, units = "secs"))))
rep("laplace", posterior::as_draws_matrix(la$draws("lt")))

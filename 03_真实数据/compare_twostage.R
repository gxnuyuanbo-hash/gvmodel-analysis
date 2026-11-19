# Two-stage comparison of model D fits: stage a (initial, under time pressure and load) vs stage b (final), same valid trials.
# Fits: fit_<smp>a_Dw.rds and fit_<smp>bm_Dw.rds for smp in s1x (experiment 1, N = 99) and s2 (experiment 2, N = 100).
# Population: posterior mean [90% interval] per stage, and the difference b - a from independent draws of the two fits.
# Persons: b_draw / d_draw (posterior draws of each person's breadth and verification); cross-stage correlation of posterior
# means, and the average within-person change with a 90% interval over draws.
# Output: logs/twostage_compare.txt
suppressMessages({library(cmdstanr); library(posterior)})
pv <- c("mu", "sigma", "gamma", "kappa", "delta", "tau", "rho"); q <- function(x) sprintf("%.2f [%.2f, %.2f]", mean(x), quantile(x, .05), quantile(x, .95))
sink("logs/twostage_compare.txt")
for (smp in c("s1x", "s2")) {
  fa <- readRDS(paste0("fit_", smp, "a_Dw.rds")); fb <- readRDS(paste0("fit_", smp, "bm_Dw.rds"))
  cat("==", smp, "\nConvergence: max rhat a", round(max(fa$summary(pv)$rhat), 3), " b", round(max(fb$summary(pv)$rhat), 3),
      "; min ess_bulk a", round(min(fa$summary(pv)$ess_bulk)), " b", round(min(fb$summary(pv)$ess_bulk)),
      "; divergent a", sum(fa$diagnostic_summary()$num_divergent), " b", sum(fb$diagnostic_summary()$num_divergent), "\n")
  da <- as_draws_matrix(fa$draws(pv)); db <- as_draws_matrix(fb$draws(pv)); n <- min(nrow(da), nrow(db))
  for (v in pv) cat(sprintf("  %-6s stage a %s | stage b %s | b - a %s\n", v, q(da[, v]), q(db[, v]), q(db[1:n, v] - da[1:n, v])))
  ba <- as_draws_matrix(fa$draws("b_draw")); bb <- as_draws_matrix(fb$draws("b_draw"))
  xa <- as_draws_matrix(fa$draws("d_draw")); xb <- as_draws_matrix(fb$draws("d_draw"))
  cat("  persons: r(breadth a, b) =", round(cor(colMeans(ba), colMeans(bb)), 3), "; r(verification a, b) =", round(cor(colMeans(xa), colMeans(xb)), 3), "\n")
  cat("  mean within-person change b - a: breadth", q(rowMeans(bb[1:n, ] - ba[1:n, ])), "; verification", q(rowMeans(xb[1:n, ] - xa[1:n, ])), "\n")
  cat("  share of persons whose 90% interval of change excludes 0: breadth",
      round(mean(apply(bb[1:n, ] - ba[1:n, ], 2, function(z) quantile(z, .05) > 0 | quantile(z, .95) < 0)), 3), "; verification",
      round(mean(apply(xb[1:n, ] - xa[1:n, ], 2, function(z) quantile(z, .05) > 0 | quantile(z, .95) < 0)), 3), "\n")
}
sink(); cat(readLines("logs/twostage_compare.txt"), sep = "\n")

# Recompute, for the final generation-verification fits (fit_<smp>_Dw.rds), the breadth reliability and the
# correlations of person posterior means with person accuracy reported in Section 4.3. Output: logs/recheck_breadth_acc.txt
suppressMessages({library(cmdstanr); library(posterior)})
sink("logs/recheck_breadth_acc.txt", split = TRUE)
for (smp in c("s1x", "s2", "pre")) {
  f <- readRDS(paste0("fit_", smp, "_Dw.rds")); d <- jsonlite::fromJSON(paste0("stan_", smp, "_prod_w.json"))
  B <- as_draws_matrix(f$draws("b_draw")); V <- as_draws_matrix(f$draws("d_draw"))
  pm <- colMeans(B); pv <- apply(B, 2, var); vm <- colMeans(V)
  y <- d$yk; acc <- rowSums(sweep(y, 2, d$nsol, `<=`) & y >= 1) / rowSums(y >= 0)
  cat(sprintf("%-4s N = %3d  breadth reliability %.3f  r(breadth, acc) %.3f  r(verification, acc) %.3f  r(breadth, verification) %.3f\n",
              smp, d$N, var(pm) / (var(pm) + mean(pv)), cor(pm, acc), cor(vm, acc), cor(pm, vm)))
}
sink()
# partial correlation of breadth with accuracy, controlling for verification ability
sink("logs/recheck_breadth_acc.txt", append = TRUE, split = TRUE)
for (smp in c("s1x", "s2", "pre")) {
  f <- readRDS(paste0("fit_", smp, "_Dw.rds")); d <- jsonlite::fromJSON(paste0("stan_", smp, "_prod_w.json"))
  pm <- colMeans(as_draws_matrix(f$draws("b_draw"))); vm <- colMeans(as_draws_matrix(f$draws("d_draw")))
  y <- d$yk; acc <- rowSums(sweep(y, 2, d$nsol, `<=`) & y >= 1) / rowSums(y >= 0)
  cat(sprintf("%-4s partial r(breadth, acc | verification) %.3f\n", smp, cor(resid(lm(pm ~ vm)), resid(lm(acc ~ vm)))))
}
sink()

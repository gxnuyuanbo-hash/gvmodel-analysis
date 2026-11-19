# Person-level PSIS-LOO comparison of versions A-D (log_lik = marginal likelihood of each person's 24 responses),
# plus posterior predictive summaries. Output: logs/compare_wide.txt
suppressMessages({library(cmdstanr); library(loo); library(jsonlite)})
sink(Sys.getenv("OUT", "logs/compare_wide.txt"), split = TRUE)
for (smp in strsplit(Sys.getenv("SMPS", "s1 s2 pre"), " ")[[1]]) {
  cat("\n==========", smp, "==========\n"); L <- list(); tab <- NULL
  for (v in c("A", "B", "C", "D")) {
    f <- readRDS(paste0("fit_", smp, "_", v, "w.rds")); ll <- f$draws("log_lik", format = "draws_matrix")
    L[[v]] <- loo(ll, r_eff = relative_eff(exp(ll), chain_id = rep(1:4, each = nrow(ll) / 4)))
    d <- fromJSON(paste0("stan_", smp, if (v == "A") "_sum_w.json" else "_prod_w.json")); N <- d$N; J <- d$J; ns <- d$nsol; yk <- d$yk
    corr <- function(y) { m <- matrix(NA, N, J); for (j in 1:J) m[, j] <- ifelse(y[, j] < 0, NA, as.integer(y[, j] >= 1 & y[, j] <= ns[j])); m }
    oc <- corr(yk); yr <- f$draws("yrep", format = "draws_matrix"); sel <- seq(1, nrow(yr), length.out = 400)
    pa <- pi <- numeric(0); ps <- numeric(0); pim <- matrix(0, 400, J)
    for (s in seq_along(sel)) { y <- matrix(as.integer(yr[sel[s], ]), N, J); y[yk < 0] <- -1; c <- corr(y)
      pa[s] <- mean(c, na.rm = TRUE); ps[s] <- sd(rowMeans(c, na.rm = TRUE)); pim[s, ] <- colMeans(c, na.rm = TRUE) }
    b <- f$draws("b_draw", format = "draws_matrix"); pm <- colMeans(b); pv <- apply(b, 2, var)
    sm <- f$summary(c("mu", "sigma", "gamma", "kappa", "delta", "tau", "rho"))
    tab <- rbind(tab, data.frame(ver = v, elpd = round(L[[v]]$estimates["elpd_loo", 1], 1), se = round(L[[v]]$estimates["elpd_loo", 2], 1),
      k_gt_.7 = sum(pareto_k_values(L[[v]]) > .7), maxRhat = round(max(sm$rhat, na.rm = TRUE), 3), minESS = round(min(sm$ess_bulk, na.rm = TRUE)),
      acc_obs = round(mean(oc, na.rm = TRUE), 3), acc_pred = round(mean(pa), 3), item_r = round(cor(colMeans(oc, na.rm = TRUE), colMeans(pim)), 2),
      sdP_obs = round(sd(rowMeans(oc, na.rm = TRUE)), 3), sdP_lo = round(quantile(ps, .05), 3), sdP_hi = round(quantile(ps, .95), 3),
      rel_b = round(var(pm) / (var(pm) + mean(pv)), 2), p_clamp = round(mean(f$draws("p_clamped")), 4)))
  }
  print(tab, row.names = FALSE); cat("\nloo_compare:\n"); print(loo_compare(L))
}
sink()

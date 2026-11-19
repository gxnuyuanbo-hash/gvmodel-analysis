# Recovery summary for model D. Output: out/recovery_summary.txt
pop <- do.call(rbind, lapply(list.files("out", "^pop_.*csv$", full.names=TRUE), read.csv, check.names=FALSE))
per <- do.call(rbind, lapply(list.files("out", "^person_.*csv$", full.names=TRUE), read.csv))
sink("out/recovery_summary.txt", split=TRUE)
nd <- length(unique(pop$dataset)); cat("datasets:", nd, "\n")
cat("convergence: max Rhat", round(max(pop$rhat), 3), "| datasets with any Rhat > 1.01:", length(unique(pop$dataset[pop$rhat > 1.01])),
    "| min bulk ESS", round(min(pop$ess_bulk)), "| min tail ESS", round(min(pop$ess_tail)), "| datasets with divergences:", sum(tapply(pop$divergent, pop$dataset, max) > 0),
    "| median fit time", round(median(pop$time)), "s\n\n")
cat("Population parameters (truth drawn uniformly across a plausible range):\n")
res <- do.call(rbind, lapply(split(pop, pop$variable), function(x) data.frame(param=x$variable[1],
  r_true_est=round(cor(x$truth, x$mean), 3), bias=round(mean(x$mean - x$truth), 3), rmse=round(sqrt(mean((x$mean - x$truth)^2)), 3),
  cover90=round(mean(x$truth >= x$`5%` & x$truth <= x$`95%`), 2), mean_ci_width=round(mean(x$`95%` - x$`5%`), 3))))
print(res[c("mu","sigma","gamma","kappa","delta","tau","rho"), ], row.names=FALSE)
cat("\nPerson parameters (pooled over datasets; r is the median of within-dataset correlations):\n")
ws <- function(t, m) median(sapply(split(seq_len(nrow(per)), per$dataset), function(i) cor(per[i, t], per[i, m])))
cat("breadth b: median r", round(ws("b_true", "b_mean"), 3), "| 90% coverage", round(mean(per$b_true >= per$b_q5 & per$b_true <= per$b_q95), 3), "\n")
cat("verification d: median r", round(ws("d_true", "d_mean"), 3), "| 90% coverage", round(mean(per$d_true >= per$d_q5 & per$d_true <= per$d_q95), 3), "\n")
cat("cross-talk: median r(b_true, d_mean)", round(ws("b_true", "d_mean"), 3), "| median r(d_true, b_mean)", round(ws("d_true", "b_mean"), 3), "\n")
# breadth recovery by region of the breadth scale
per$zone <- cut(per$b_true, c(-Inf, -4, -1, 2, Inf), labels=c("< -4", "-4..-1", "-1..2", "> 2"))
cat("\nBreadth error by true breadth zone:\n"); print(aggregate(cbind(abs_err = abs(b_mean - b_true), cover = (b_true >= b_q5 & b_true <= b_q95), width = b_q95 - b_q5) ~ zone, per, function(v) round(mean(v), 3)))
sink()

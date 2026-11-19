# Follow-up diagnostics for the 100-dataset recovery pilot (model D).
suppressMessages(library(data.table))
pop <- rbindlist(lapply(Sys.glob("out/pop_*.csv"), fread))
per <- rbindlist(lapply(Sys.glob("out/person_*.csv"), fread, colClasses=list(character="dataset")))
cat("Lowest tail ESS rows:\n"); print(pop[order(ess_tail)][1:5, .(dataset, variable, rhat, ess_bulk, ess_tail)])
cat("\nRhat > 1.01 rows:\n"); print(pop[rhat > 1.01, .(dataset, variable, rhat, ess_bulk, ess_tail)])
# Cross-talk, properly: within-dataset correlation of estimation errors, and true vs estimated b-d correlation
ct <- per[, .(err_r = cor(b_mean - b_true, d_mean - d_true),
              r_true = cor(b_true, d_true), r_est = cor(b_mean, d_mean)), by=dataset]
cat("\nMedian within-dataset r(b error, d error):", round(median(ct$err_r), 3), "\n")
cat("r across datasets between true and estimated person-level b-d correlation:", round(cor(ct$r_true, ct$r_est), 3), "\n")
# Upper-breadth zone: shrinkage direction
per[, zone := cut(b_true, c(-Inf, -4, -1, 2, Inf), labels=c("< -4", "-4..-1", "-1..2", "> 2"))]
cat("\nSigned error and n by zone:\n"); print(per[, .(n=.N, signed_err=round(mean(b_mean - b_true), 3), below_ci=round(mean(b_true > b_q95), 3), above_ci=round(mean(b_true < b_q5), 3)), by=zone][order(zone)])
